from pymongo import MongoClient
from config import SysConfig
from Models.chat_model import ChatModel

class ChatDAO:
    def __init__(self):
        client = MongoClient(SysConfig.MONGO_CONNECTION_STRING)
        self.db = client.get_database(SysConfig.DB_NAME)
        self.chats_collection = self.db.chats

    def find_chat_by_user_id(self, user_id):
        """Find the chat document that belongs to a specific user_id."""
        chat_data = self.chats_collection.find_one({'user_id': user_id})
        if chat_data:
            return ChatModel.from_dict(chat_data)
        return None

    def get_messages_sent(self, chat_id):
        """Retrieve messages sent by the user from the corresponding chat document."""
        chat = self.chats_collection.find_one({"chat_id": chat_id})
        if chat:
            return chat.get("messages_sent", [])
        return None
    
    def get_messages_received(self, chat_id):
        """Retrieve messages received by the user from the corresponding chat document."""
        chat = self.chats_collection.find_one({"chat_id": chat_id})
        if chat:
            return chat.get("messages_received", [])
        return None

    def get_chat_by_user_id(self, user_id):
        """
        Retrieve the chat_id associated with the given user_id.
        Returns None if no chat document exists for this user.
        """
        chat = self.chats_collection.find_one({"user_id": user_id})
        if chat:
            return chat.get("chat_id")
        return None  

    def get_chats_by_user_id(self, user_id):
        """Retrieve all chat IDs and titles associated with a user."""
        chats = self.chats_collection.find({"user_id": user_id}, 
                                           {"chat_id": 1, "title": 1, "_id": 0,
                                            "messages_sent": 1, "messages_received": 1}, sort=[("chat_id", 1)])
        chats_list = list(chats)
        return chats_list


    def add_user_message(self, chat_id, sender_id: int, message: str):
        """
        Adds a sent message to the correct chat document where chat_id and user_id match.

        - `chat_id` (int): The chat document ID.
        - `sender_id` (int): The user sending the message.
        - `message` (str): The message content.

        Returns `True` if successful, `False` otherwise.
        """
        result = self.chats_collection.update_one(
            {"chat_id": chat_id, "user_id": sender_id},  
            {"$push": {"messages_sent": message}}  
        )
    
        return result.modified_count > 0 
    
    def add_bot_message(self, chat_id, logged_user_id: int, message: str):
        """
        Adds a sent message to the correct chat document where chat_id and user_id match.

        - `chat_id` (int): The chat document ID.
        - `logged_user_id` (int): The user whose chat this will be stored in.
        - `message` (str): The message content.

        Returns `True` if successful, `False` otherwise.
        """
        result = self.chats_collection.update_one(
            {"chat_id": chat_id, "user_id": logged_user_id},  
            {"$push": {"messages_received": message}}  
        )
    
        return result.modified_count > 0  
    
    def add_new_chat(self, user_id):
        """
        Creates a new chat document for a user if one does not already exist.
        """
        existing_chat = self.chats_collection.find_one({"user_id": user_id})

        if existing_chat:
            return existing_chat["chat_id"]

        new_chat_id = self.generate_chat_id()

        new_chat = {
            "chat_id": new_chat_id,
            "user_id": user_id,
            "messages_sent": [],
            "messages_received": []
        }

        self.chats_collection.insert_one(new_chat)
        return new_chat_id

    def generate_chat_id(self):
        """
        Generate a unique chat_id based on the highest existing chat_id.
        """
        last_chat = self.chats_collection.find_one({}, sort=[("chat_id", -1)])
        if last_chat:
            return last_chat["chat_id"] + 1
        return 1  