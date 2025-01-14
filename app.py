from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)
key = os.getenv("ENCRYPTION_KEY")
if not key:
    raise ValueError("Encryption key not found in environment variables")
fernet = Fernet(key)

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

        encrypted_pwd = fernet.encrypt(pwd.encode())
        # NEED TO HASH PASSWORD HERE 
        users_data['users'].append(user)
        users_data['emails'].append(email)
        users_data['passwords'].append(encrypted_pwd)  

        with open('users.json', 'w') as f:
            json.dump(users_data, f)

        return jsonify({'message': 'User registered successfully'}), 200

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
            if fernet.decrypt(users_data['passwords'][user_index]).decode() == pwd: 
                return jsonify({'message': 'Login successful', 'username': login}), 200
            else:
                return jsonify({'message': 'Invalid password'}), 401


        elif login in users_data['emails']:
            user_index = users_data['emails'].index(login)
            if fernet.decrypt(users_data['passwords'][user_index]).decode() == pwd:  
                username = users_data['users'][user_index] 
                return jsonify({'message': 'Login successful', 'username': username}), 200
            else:
                return jsonify({'message': 'Invalid password'}), 401

        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the API!'}), 200

if __name__ == '__main__':
    app.run(debug=True)