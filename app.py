from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
from Logic.user_bl import UserBL 
from Logic.chat_bl import ChatBL
from datetime import timedelta
from config import SysConfig
import uuid
from llama_cpp import Llama
import chromadb
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.secret_key = SysConfig.SECRET_KEY

app.config['SESSION_PERMANENT'] = False 
app.config['SESSION_TYPE'] = 'filesystem'  
app.config['SESSION_COOKIE_NAME'] = 'my_session'
app.config['SESSION_COOKIE_HTTPONLY'] = True  
app.config['SESSION_COOKIE_SECURE'] = True  
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' 
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
Session(app)

CORS(app, supports_credentials=True, origins=SysConfig.FRONT_END_URL)
user_service = UserBL()
chat_bl = ChatBL()
executor = ThreadPoolExecutor()

llm_biomistral = Llama.from_pretrained(
    repo_id="mradermacher/BioMistral-7B-SLERP-GGUF",
    filename="BioMistral-7B-SLERP.Q5_K_M.gguf",
)

llm_meditron = Llama.from_pretrained(
    repo_id="TheBloke/meditron-7B-GGUF",
    filename="meditron-7b.Q5_K_M.gguf",
)
chroma_client = chromadb.PersistentClient(path="./medical_db")
collection = chroma_client.get_or_create_collection("blood_analysis")

def build_prompt(question, context):
    return (
        "You are a medical assistant. Answer clearly and briefly.\n"
        "Limit your response to 4 concise sentences. Avoid repetition.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\nAnswer:"
    )


def get_context(prompt):
    results = collection.query(query_texts=[prompt], n_results=1)
    docs = results["documents"][0] if results["documents"] else []
    return "\n".join(docs) if docs else "No relevant medical context found."

@app.route('/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json()
    username = data.get('user')
    email = data.get('email')
    password = data.get('pwd')
    message, status_code = user_service.sign_up(username, email, password)
    return jsonify(message), status_code

@app.route('/log-in', methods=['POST'])
def log_in():
    data = request.get_json()
    login = data.get('login')
    password = data.get('pwd')
    message, status_code = user_service.log_in(login, password)

    if status_code == 200:
        session['user_id'] = message.get('user_id')  
        session['username'] = message.get('username') 
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True  
    return jsonify(message), status_code

@app.route('/log-out', methods=['POST'])
def log_out():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/google-login', methods=['POST'])
def google_login():
    data = request.get_json()
    token = data.get('credential')
    message, status_code = user_service.google_login(token)
    return jsonify(message), status_code

@app.route('/edit-account', methods=['POST'])
def edit_account():
    data = request.get_json()
    user_id = data.get('id')
    username = data.get('username')
    email = data.get('email')
    message, status_code = user_service.edit_account(user_id, username, email)
    return jsonify(message), status_code

@app.route('/get-google-client-id', methods=['GET'])
def get_google_client_id():
    message, status_code = user_service.fetch_google_client_id()
    return jsonify(message), status_code

@app.route('/get-id-for-username', methods=['OPTIONS','POST'])
def get_user_id_for_username():
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({'message': 'Username is required'}), 400

    user_id = user_service.get_id_by_username(username)
    if user_id:
        return jsonify({'id': user_id}), 200  
    else:
        return jsonify({'message': 'User not found'}), 404
    

@app.route('/get-account', methods=['POST'])
def get_account_details():
    data = request.get_json()
    user_id = data.get('id')  
    if not user_id:
        return jsonify({'message': 'User ID is required'}), 400

    message, status_code = user_service.get_account_details(user_id)
    if status_code == 200:
        return jsonify({
            'id': message.get('id'),
            'username': message.get('username'),
            'email': message.get('email')
        }), 200
    else:
        return jsonify(message), status_code

@app.route('/start-chat', methods=['POST'])
def start_chat():
    data = request.get_json()
    user_ids = data.get("user_ids")
    
    if not user_ids:
        return jsonify({"message": "User IDs are required"}), 400

    response = chat_bl.start_new_chat(user_ids)
    return jsonify(response), 200

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()  
    chat_id = data.get("chat_id") 
    message = data.get("message")
    sender_id = data.get("sender_id")
    
    if not chat_id or not message or not sender_id:
        return jsonify({"message": "Chat ID, message, and sender ID are required"}), 400
    
    response = chat_bl.send_user_message(chat_id, message, sender_id)
    return jsonify(response), 200

@app.route('/get-bot-response', methods=['POST'])
def get_bot_response():
    data = request.get_json()
    chat_id = data.get("chat_id")
    user_prompt = data.get("message")

    if not chat_id or not user_prompt:
        return jsonify({"message": "chat_id and message are required"}), 400

    context = get_context(user_prompt)
    full_prompt = build_prompt(user_prompt, context)
    result = llm_biomistral(full_prompt,max_tokens=250,temperature=0.3,stop=["\n\n", "Question:", "Context:", "Limit your response"])
    bot_reply = result['choices'][0]['text'].strip()

    user_id = session.get("user_id")
    if user_id:
        chat_bl.dao.add_bot_message(chat_id, user_id, bot_reply)

    return jsonify({"response": bot_reply}), 200

def run(model, prompt):
    try:
        result = model(
            prompt,
            max_tokens=150,
            temperature=0.3,
            stop=["\n\n", "Question:", "Context:", "Limit your response"]
        )
        return result.get('choices', [{}])[0].get('text', '').strip() or "No response."
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/models-replies', methods=['POST'])
def compare_models():
    data = request.get_json()
    prompt = data.get("message")
    chat_id = data.get("chat_id")

    if not prompt or not chat_id:
        return jsonify({"message": "Missing message or chat_id"}), 400

    context = get_context(prompt)
    full_prompt = build_prompt(prompt, context)

    future_bio = executor.submit(run, llm_biomistral, full_prompt)
    future_medi = executor.submit(run, llm_meditron, full_prompt)

    response_bio = future_bio.result()
    response_medi = future_medi.result()

    return jsonify({
        "biomistral": response_bio,
        "meditron": response_medi
    }), 200
    
@app.route('/create-chat', methods=['POST'])
def create_chat():
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400
    chat_id = chat_bl.start_new_chat(user_id)
    return jsonify({"chat_id": chat_id}), 201

@app.route('/get-chat-id/<int:user_id>', methods=['OPTIONS', 'GET'])
def get_chat_by_user_id(user_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    chat = chat_bl.get_chat_id(user_id)
    if chat is not None:  
        return jsonify({"chat_id": chat}), 200
    else:
        print("Creating new chat")
        response = chat_bl.start_new_chat(user_id)
        if response:  
            return jsonify({"chat_id": response}), 201
        else:
            return jsonify({"message": "Failed to create chat"}), 500

@app.route('/restore-chat-history/<int:chat_id>', methods=['GET'])
def get_messages(chat_id):
    messages = chat_bl.get_messages(chat_id)

    if not messages or ('messages_sent' not in messages or 'messages_received' not in messages):
        return jsonify({"message": "Chat not found or no messages available"}), 404

    return jsonify(messages), 200

@app.route('/get-chat-id/<int:user_id>', methods=['GET'])
def get_chat_id_only(user_id):
    chat = chat_bl.get_chat_by_user_id(user_id)

    if chat:
        return jsonify({"chat_id": chat['chat_id']}), 200
    else:
        response = chat_bl.create_new_chat([user_id])
        if response:
            return jsonify({"chat_id": response['chat_id']}), 201
        else:
            return jsonify({"message": "Failed to create chat"}), 500

@app.route('/get-user-chats/<int:user_id>', methods=['GET'])
def get_user_chats(user_id):
    chats = chat_bl.get_user_chats(user_id)
    if chats:
        return jsonify({"chats": chats}), 200
    return jsonify({"message": "No chats found"}), 404


@app.before_request
def check_session_expiration():
    session.permanent = False
    session.modified = True
    
    if request.method == 'OPTIONS':
        return '', 200

    if request.endpoint not in ['log_in', 'sign_up', 'google_login', 'get_google_client_id', 'static']:
        if 'user_id' not in session:
            if request.endpoint == 'home':  
                return jsonify({'message': 'Session expired', 'expired': True}), 200
            else:
                return jsonify({'message': 'Session expired'}), 401
            
@app.before_request
def enforce_session_timeout():
    """Invalidate the session if it exceeds the absolute timeout."""
    if 'session_id' in session:
        session.modified = True 
    else:
        session.clear()

@app.route('/home', methods=['GET'])
def home():
    return jsonify({'message': f"Welcome back, {session['username']}!"}), 200

@app.route('/', methods=['GET'])
def default():
    return jsonify({'message': 'Welcome to the API!'}), 200

if __name__ == '__main__':
    app.run(debug=True)