from flask import Flask, request, jsonify
from flask_cors import CORS
from Logic.user_bl import UserBL 

app = Flask(__name__)
CORS(app)
user_service = UserBL()

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
    return jsonify(message), status_code

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

@app.route('/get-id-for-username', methods=['POST'])
def get_user_id_for_username():
    data = request.get_json()
    username = data.get('username')
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

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the API!'}), 200


if __name__ == '__main__':
    app.run(debug=True)