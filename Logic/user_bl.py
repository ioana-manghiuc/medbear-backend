import bcrypt
from google.auth.transport import requests
from google.oauth2 import id_token
from config import Config
from Database.user_dao import UserDAO

class UserBL:
    def __init__(self):
        self.dao = UserDAO()

    def sign_up(self, username, email, password):
        if not username or not email or not password:
            return {'message': 'All fields are required'}, 400

        user_data = self.dao.find_all_user_data()

        if user_data:
            if username in user_data['usernames']:
                return {'message': 'Username already exists'}, 409
            if email in user_data['emails']:
                return {'message': 'Email already exists'}, 409

        hashed_pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_id = self.dao.add_new_user(username, email, hashed_pwd)
        return {'message': 'User registered successfully', 'id': user_id}, 200

    def log_in(self, login, password):
        user_data = self.dao.find_all_user_data()
        if not user_data:
            return {'message': 'User data not found'}, 404

        if login in user_data['usernames']:
            index = user_data['usernames'].index(login)
        elif login in user_data['emails']:
            index = user_data['emails'].index(login)
        else:
            return {'message': 'Invalid credentials'}, 401

        hashed_pwd = user_data['passwords'][index]
        if bcrypt.checkpw(password.encode(), hashed_pwd.encode()):
            user_id = user_data['ids'][index]  
            return {
                'message': 'Login successful',
                'username': user_data['usernames'][index],
                'user_id': user_id
            }, 200
        return {'message': 'Invalid credentials'}, 401

    def google_login(self, token):
        if not token:
            return {'message': 'Google token is required'}, 400

        try:
            id_info = id_token.verify_oauth2_token(token, requests.Request(), Config.GOOGLE_CLIENT_ID)
            email = id_info.get('email')
            username = email.split('@')[0]

            user_data = self.dao.find_all_user_data()
            if user_data and email in user_data['emails']:
                index = user_data['emails'].index(email)
                username = user_data['usernames'][index]
                return {'message': 'Login successful', 'username': username, 'email': email}, 200
            else:
                user_id = self.dao.add_google_user(username, email)
                return {'message': 'User registered successfully', 'id': user_id, 'username': username, 'email': email}, 200
        except ValueError as e:
            return {'message': 'Invalid Google token', 'details': str(e)}, 401

    def edit_account(self, user_id, username, email):
        user_data = self.dao.find_all_user_data()
        if not user_data:
            return {'message': 'User not found'}, 404

        self.dao.update_user_account(user_id, username, email)
        return {'message': 'Account updated successfully'}, 200

    def fetch_google_client_id(self):
        client_id = Config.GOOGLE_CLIENT_ID
        if client_id:
            return {'googleClientId': client_id}, 200
        return {'message': 'Client ID not found'}, 404

    def get_user_by_username(self, username):
        user_data = self.dao.find_user_by_username(username)
        if not user_data:
            return {'message': 'User not found'}, 404

        return {
            'id': user_data.get('ids'),
            'username': user_data.get('usernames'),
            'email': user_data.get('emails'),
        }, 200

    def get_id_by_username(self, username):
        user_id = self.dao.find_id_by_username(username)
        if user_id:
            return user_id  
        return None  

    def get_account_details(self, user_id):
        user_data = self.dao.find_user_by_id(user_id)
        if user_data:
            return {
                'id': user_data.user_id,
                'username': user_data.username,
                'email': user_data.email,
                'password': user_data.password,
            }, 200
        else:
            return {'message': 'User not found'}, 404