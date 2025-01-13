from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app, resources={r"/sign-up": {"origins": "http://localhost:5173"}})

@app.route('/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json()
    
    # Extract user details
    user = data.get('user')
    email = data.get('email')
    pwd = data.get('pwd')
    
    # Example: You can add your logic here to check if username/email exists
    try:
        with open('users.json', 'r') as f:
            users_data = json.load(f)
        
        if user in users_data['users']:
            return jsonify({'message': 'Username already exists'}), 409
        if email in users_data['emails']:
            return jsonify({'message': 'Email already exists'}), 409

        # Save new user data (you may want to hash the password in a real app)
        users_data['users'].append(user)
        users_data['emails'].append(email)
        users_data['passwords'].append(pwd)  # Don't store passwords in plain text!

        with open('users.json', 'w') as f:
            json.dump(users_data, f)

        return jsonify({'message': 'User registered successfully'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)