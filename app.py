from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import bcrypt
from dotenv import load_dotenv
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)
client = MongoClient(os.getenv('MONGO_URI'))
CORS(app)

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

@app.route('/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json()
    
    user = data.get('user')
    email = data.get('email')
    pwd = data.get('pwd')

    try:
        with open('users.json', 'r') as f:
            users_data = json.load(f)

        if user in users_data['users']:
            return jsonify({'message': 'Username already exists'}), 409
        if email in users_data['emails']:
            return jsonify({'message': 'Email already exists'}), 409

        new_id = users_data['ids'][-1] + 1 if users_data['ids'] else 1

        users_data['ids'].append(new_id)
        users_data['users'].append(user)
        users_data['emails'].append(email)
        hashed_pwd = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
        users_data['passwords'].append(hashed_pwd)

        with open('users.json', 'w') as f:
            json.dump(users_data, f, indent=4)

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
        with open('users.json', 'r') as f:
            users_data = json.load(f)

        if login in users_data['users']:
            user_index = users_data['users'].index(login)
            if bcrypt.checkpw(pwd.encode(), users_data['passwords'][user_index].encode()):
                return jsonify({'message': 'Login successful', 'username': login}), 200
            else:
                return jsonify({'message': 'Invalid password'}), 401

        elif login in users_data['emails']:
            user_index = users_data['emails'].index(login)
            if bcrypt.checkpw(pwd.encode(), users_data['passwords'][user_index].encode()):
                username = users_data['users'][user_index]
                return jsonify({'message': 'Login successful', 'username': username}), 200
            else:
                return jsonify({'message': 'Invalid password'}), 401

        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500

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

        with open('users.json', 'r') as f:
            users_data = json.load(f)

        if email in users_data['emails']:
            user_index = users_data['emails'].index(email)
            username = users_data['users'][user_index]
            return jsonify({'message': 'Login successful', 'username': username, 'email': email}), 200
        else:
            new_id = users_data['ids'][-1] + 1 if users_data['ids'] else 1
            users_data['ids'].append(new_id)
            users_data['users'].append(username)
            users_data['emails'].append(email)
            users_data['passwords'].append(None)  

            with open('users.json', 'w') as f:
                json.dump(users_data, f, indent=4)

            return jsonify({'message': 'User registered successfully', 'username': username, 'email': email}), 200

    except ValueError as e:
        return jsonify({'message': 'Invalid Google token', 'details': str(e)}), 401

@app.route('/edit-account', methods=['POST'])
def edit_account():
    data = request.get_json()
    user_id = data.get('id')
    username = data.get('username')
    email = data.get('email')

    if user_id is None or username is None or email is None:
        return jsonify({'message': 'ID, username, and email are required'}), 400

    try:
        with open('users.json', 'r') as f:
            users_data = json.load(f)

        if user_id not in users_data['ids']:
            return jsonify({'message': 'User ID not found'}), 404

        user_index = users_data['ids'].index(user_id)

        if email in users_data['emails'] and users_data['emails'][user_index] != email:
            return jsonify({'message': 'Email already in use by another user'}), 409

        users_data['users'][user_index] = username
        users_data['emails'][user_index] = email

        with open('users.json', 'w') as f:
            json.dump(users_data, f, indent=4)

        return jsonify({'message': 'Account updated successfully'}), 200

    except FileNotFoundError:
        return jsonify({'message': 'User data file not found'}), 500
    except json.JSONDecodeError:
        return jsonify({'message': 'Error decoding user data file'}), 500
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500


@app.route('/get-account', methods=['POST'])
def get_account():
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({'message': 'Username is required'}), 400

    try:
        with open('users.json', 'r') as f:
            users_data = json.load(f)

        if username in users_data['users']:
            user_index = users_data['users'].index(username)
            user_id = users_data['ids'][user_index]
            email = users_data['emails'][user_index]
            return jsonify({'id': user_id, 'username': username, 'email': email}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the API!'}), 200

if __name__ == '__main__':
    app.run(debug=True)