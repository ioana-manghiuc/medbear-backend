import bcrypt
from google.auth.transport import requests
from google.oauth2 import id_token
from config import SysConfig
from Database.user_dao import UserDAO

class UserBL:
    def __init__(self):
        self.dao = UserDAO()

    def sign_up(self, username, email, password):
        if not username or not email or not password:
            return {'message': 'All fields are required'}, 400

        existing_user = self.dao.find_user_by_username(username)
        if existing_user:
            return {'message': 'Username already exists'}, 409
        
        existing_user = self.dao.find_user_by_email(email)
        if existing_user:
            return {'message': 'Email already exists'}, 409

        hashed_pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        user_id = self.dao.add_new_user(username, email, hashed_pwd)
        return {'message': 'User registered successfully', 'id': user_id}, 200

    def log_in(self, login, password):
        user_data = self.dao.find_user_by_username(login) or self.dao.find_user_by_email(login)
        
        if not user_data:
            return {'message': 'Invalid credentials'}, 401

        if bcrypt.checkpw(password.encode(), user_data.password.encode()):
            return {
                'message': 'Login successful',
                'username': user_data.username,
                'user_id': user_data.user_id
            }, 200
        
        return {'message': 'Invalid credentials'}, 401

    def google_login(self, token):
        if not token:
            return {'message': 'Google token is required'}, 400

        try:
            id_info = id_token.verify_oauth2_token(token, requests.Request(), SysConfig.GOOGLE_CLIENT_ID)
            email = id_info.get('email')
            username = email.split('@')[0]

            existing_user = self.dao.find_user_by_email(email)
            if existing_user:
                return {'message': 'Login successful', 'username': existing_user.username, 'email': email}, 200
            else:
                user_id = self.dao.add_google_user(username, email)
                return {'message': 'User registered successfully', 'id': user_id, 'username': username, 'email': email}, 200
        except ValueError as e:
            return {'message': 'Invalid Google token', 'details': str(e)}, 401

    def edit_account(self, user_id, username, email):
        user_data = self.dao.find_user_by_id(user_id)
        if not user_data:
            return {'message': 'User not found'}, 404

        updated_user = self.dao.update_user_account(user_id, username, email)
        return {'message': 'Account updated successfully', 'username': updated_user.username, 'email': updated_user.email}, 200

    def fetch_google_client_id(self):
        client_id = SysConfig.GOOGLE_CLIENT_ID
        if client_id:
            return {'googleClientId': client_id}, 200
        return {'message': 'Client ID not found'}, 404

    def get_user_by_username(self, username):
        user_data = self.dao.find_user_by_username(username)
        if not user_data:
            return {'message': 'User not found'}, 404

        return {
            'id': user_data.user_id,
            'username': user_data.username,
            'email': user_data.email,
        }, 200

    def get_id_by_username(self, username):
        user_id = self.dao.find_id_by_username(username)

        if user_id is not None:
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