from pymongo import MongoClient
from config import SysConfig
from Models.user_model import UserModel

class UserDAO:
    def __init__(self):
        client = MongoClient(SysConfig.MONGO_CONNECTION_STRING)
        self.db = client.get_database(SysConfig.DB_NAME)
        self.users_collection = self.db.users

    def find_user_by_username(self, username):
        user_data = self.users_collection.find_one({'username': username})
        if user_data:
            return UserModel.from_dict({
                "id": user_data.get("id"),
                "username": user_data.get("username"),
                "email": user_data.get("email"),
                "password": user_data.get("password"),
            })
        return None

    def find_user_by_email(self, email):
        user_data = self.users_collection.find_one({'email': email})
        if user_data:
            return UserModel.from_dict({
                "id": user_data.get("id"),
                "username": user_data.get("username"),
                "email": user_data.get("email"),
                "password": user_data.get("password"),
            })
        return None

    def find_user_by_id(self, user_id):
        user_data = self.users_collection.find_one({'id': user_id})
        if user_data:
            return UserModel.from_dict({
                "id": user_data.get("id"),
                "username": user_data.get("username"),
                "email": user_data.get("email"),
                "password": user_data.get("password"),
            })
        return None

    def find_id_by_username(self, username):
        user = self.users_collection.find_one({'username': username})
        if user:
            return user.get('id')
        return None

    def add_new_user(self, username, email, hashed_pwd):
        new_id = self.users_collection.count_documents({}) + 1  
        self.users_collection.insert_one({
            'id': new_id,
            'username': username,
            'email': email,
            'password': hashed_pwd,
        })
        return new_id

    def update_user_account(self, user_id, username, email):
        result = self.users_collection.update_one(
            {'id': user_id},
            {'$set': {'username': username, 'email': email}}
        )
        if result.matched_count > 0:
            return UserModel(user_id, username, email)
        return None

    def add_google_user(self, username, email):
        new_id = self.users_collection.count_documents({}) + 1 
        self.users_collection.insert_one({
            'id': new_id,
            'username': username,
            'email': email,
            'password': None,  
        })
        return UserModel(new_id, username, email)