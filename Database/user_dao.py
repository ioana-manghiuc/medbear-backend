from pymongo import MongoClient
from config import SysConfig
from Models.user_model import User

class UserDAO:
    def __init__(self):
        client = MongoClient(SysConfig.MONGO_URI)
        self.db = client.get_database(SysConfig.DB_NAME)
        self.users_collection = self.db.users

    def find_user_by_username(self, username):
        user_data = self.users_collection.find_one({'usernames': username})
        if user_data:
            return User.from_dict({
                "id": user_data.get("id"),
                "username": user_data.get("usernames"),
                "email": user_data.get("emails"),
                "password": user_data.get("passwords"),
            })
        return None

    def find_user_by_email(self, email):
        user_data = self.users_collection.find_one({'emails': email})
        if user_data:
            return User.from_dict({
                "id": user_data.get("id"),
                "username": user_data.get("usernames"),
                "email": user_data.get("emails"),
                "password": user_data.get("passwords"),
            })
        return None

    def find_user_by_id(self, user_id):
        index = user_id - 1

        if index >= 0:
            user_data = self.users_collection.find_one({'ids': user_id})

            if user_data:
                user = {
                    "id": user_data.get("ids")[index] if user_data.get("ids") else None,
                    "email": user_data.get("emails")[index] if user_data.get("emails") else None,
                    "username": user_data.get("usernames")[index] if user_data.get("usernames") else None
                }

                if None not in user.values():
                    return User.from_dict(user)
                else:
                    print("User data is incomplete")
                    return None
            else:
                print("No user found in collection with this ID")
                return None
        else:
            print("Invalid user_id")
            return None

    def find_id_by_username(self, username):
        user = self.users_collection.find_one({'usernames': username})

        if user:
            try:
                index = user['usernames'].index(username)
                user_id = user['ids'][index]
                return user_id  
            except ValueError:
                return None 
        return None  

    def find_all_user_data(self):
        user_data = self.users_collection.find_one()
        if user_data:
            return {
                'ids': user_data.get('ids', []),
                'usernames': user_data.get('usernames', []),
                'emails': user_data.get('emails', []),
                'passwords': user_data.get('passwords', []),
            }
        return None

    def add_new_user(self, username, email, hashed_pwd):
        user_data = self.find_all_user_data()
        new_id = max(user_data['ids']) + 1 if user_data and user_data.get('ids') else 1
        self.users_collection.update_one(
            {},
            {
                '$push': {
                    'ids': new_id,
                    'usernames': username,
                    'emails': email,
                    'passwords': hashed_pwd,
                }
            },
            upsert=True,
        )
        return new_id

    def update_user_account(self, user_id, username, email):
        user_data = self.find_all_user_data()
        user_index = user_data['ids'].index(user_id)

        self.users_collection.update_one(
            {},
            {'$set': {f'usernames.{user_index}': username, f'emails.{user_index}': email}},
        )
        return User(user_id, username, email)

    def add_google_user(self, username, email):
        user_data = self.find_all_user_data()
        new_id = max(user_data['ids']) + 1 if user_data else 1
        self.users_collection.update_one(
            {},
            {
                '$push': {
                    'ids': new_id,
                    'usernames': username,
                    'emails': email,
                    'passwords': None,
                }
            },
            upsert=True,
        )
        return User(new_id, username, email)