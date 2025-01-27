from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import bcrypt
from dotenv_vault import load_dotenv
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)
CORS(app)
client = MongoClient(os.getenv('MONGO_URI'))
db = client.get_database('medical-ai-db')
users_collection = db.users

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

@app.route('/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json()
    
    user = data.get('user')
    email = data.get('email')
    pwd = data.get('pwd')

    if not user or not email or not pwd:
        return jsonify({'message': 'User, email, and password are required'}), 400

    try:
        user_data = users_collection.find_one()

        if user_data:
            if user in user_data['usernames']:
                return jsonify({'message': 'Username already exists'}), 409
            if email in user_data['emails']:
                return jsonify({'message': 'Email already exists'}), 409

        hashed_pwd = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

        new_id = max(user_data['ids']) + 1 if user_data else 1
        new_user = {
            'ids': [new_id],
            'usernames': [user],
            'emails': [email],
            'passwords': [hashed_pwd]
        }
        
        users_collection.update_one({}, {'$push': {'ids': new_id, 'usernames': user, 'emails': email, 'passwords': hashed_pwd}}, upsert=True)

        return jsonify({'message': 'User registered successfully', 'id': new_id}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/log-in', methods=['POST'])
def log_in():
    data = request.get_json()

    login = data.get('login') 
    pwd = data.get('pwd')      

    if not login or not pwd:
        return jsonify({'message': 'Login and password are required'}), 400

    try:
        user_data = users_collection.find_one()

        if not user_data:
            return jsonify({'message': 'No users found in the database'}), 404

        if login in user_data['usernames']:
            user_index = user_data['usernames'].index(login)
            if bcrypt.checkpw(pwd.encode(), user_data['passwords'][user_index].encode()):
                return jsonify({'message': 'Login successful', 'username': login}), 200
            else:
                return jsonify({'message': 'Invalid password'}), 401

        elif login in user_data['emails']:
            user_index = user_data['emails'].index(login)
            if bcrypt.checkpw(pwd.encode(), user_data['passwords'][user_index].encode()):
                username = user_data['usernames'][user_index]
                return jsonify({'message': 'Login successful', 'username': username}), 200
            else:
                return jsonify({'message': 'Invalid password'}), 401

        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/get-google-client-id', methods=['GET'])  
def get_google_client_id():
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    if client_id:
        return jsonify({'googleClientId': client_id}), 200
    else:
        return jsonify({'message': 'Client ID not found'}), 404

@app.route('/google-login', methods=['POST'])
def google_login():
    data = request.get_json()
    token = data.get("credential")

    if not token:
        return jsonify({'message': 'Google token is required'}), 400

    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        email = id_info.get('email')
        username = email.split('@')[0]

        user_data = users_collection.find_one()

        if user_data:
            if email in user_data['emails']:
                user_index = user_data['emails'].index(email)
                username = user_data['usernames'][user_index]
                return jsonify({'message': 'Login successful', 'username': username, 'email': email}), 200
            else:
                new_id = max(user_data['ids']) + 1 if user_data['ids'] else 1
                users_collection.update_one({}, {'$push': {'ids': new_id, 'usernames': username, 'emails': email, 'passwords': None}}, upsert=True)
                return jsonify({'message': 'User registered successfully', 'username': username, 'email': email}), 200

    except ValueError as e:
        return jsonify({'message': 'Invalid Google token', 'details': str(e)}), 401

@app.route('/edit-account', methods=['POST'])
def edit_account():
    data = request.get_json()
    user_id = data.get('id')
    username = data.get('username')
    email = data.get('email')

    if not user_id or not username or not email:
        return jsonify({'message': 'ID, username, and email are required'}), 400

    try:
        user_data = users_collection.find_one()

        if not user_data:
            return jsonify({'message': 'User ID not found'}), 404

        user_index = user_data['ids'].index(user_id)

        if email in user_data['emails'] and email != user_data['emails'][user_index]:
            return jsonify({'message': 'Email already in use by another user'}), 409

        users_collection.update_one(
            {},
            {'$set': {
                f'usernames.{user_index}': username,
                f'emails.{user_index}': email
            }}
        )

        return jsonify({'message': 'Account updated successfully'}), 200

    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500

@app.route('/get-id-for-username', methods=['GET'])
def get_id_for_username():
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({'message': 'Username is required'}), 400

    try:
        user_data = users_collection.find_one({'usernames': username})

        if not user_data:
            return jsonify({'message': 'User not found'}), 404

        user_index = user_data['usernames'].index(username)
        user_id = user_data['ids'][user_index]
        return jsonify({'id': user_id, 'username': username, 'email': user_data['emails'][user_index]}), 200

    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500

@app.route('/get-account', methods=['GET'])
def get_account():
    data = request.get_json()
    print("Received data:", data) 

    user_id = data.get('id')
    if not user_id:
        return jsonify({'message': 'User ID is required'}), 400

    try:
        user_data = users_collection.find_one({'ids': user_id})

        if not user_data:
            return jsonify({'message': 'User not found'}), 404

        user_index = user_data['ids'].index(user_id)
        return jsonify({
            'id': user_data['ids'][user_index],
            'email': user_data['emails'][user_index],
            'username': user_data['usernames'][user_index]
        }), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the API!'}), 200

if __name__ == '__main__':
    app.run(debug=True)