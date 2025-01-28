from pymongo import MongoClient
from config import Config
from Models.chat import Chat

class ChatDAO:
    def __init__(self):
        client = MongoClient(Config.MONGO_URI)
        self.db = client.get_database(Config.DB_NAME)
        self.chats_collection = self.db.chats

    def find_chat_by_user_id(self, user_id):
        """Find the chat by user_id (return the first chat the user is part of)."""
        chat_data = self.chats_collection.find_one({'user_ids': user_id})
        if chat_data:
            return Chat.from_dict(chat_data)
        return None

    def get_messages_sent(self, chat_id):
        """Retrieve the messages_sent at the correct index for the given chat_id."""
        chat = self.chats_collection.find_one({"ids": chat_id})
        print(chat)
        if chat:
            chat_index = chat["ids"].index(chat_id)
            messages_sent = chat.get("messages_sent", [])

            if chat_index < len(messages_sent):
                return messages_sent[chat_index]
            else:
                return []  
        return None 
    
    def get_chat_by_user_id(self, user_id):
        """
        Fetch the chat associated with the user_id from MongoDB.
        Return the chat_id from the "ids" field corresponding to the user_id's index in "user_ids".
        If no chat is found, return None or -1 if no chat is found.
        """
        try:
            chat = self.chats_collection.find_one({
                "user_ids": user_id  
            })
        
            if chat:
                user_index = chat["user_ids"].index(user_id)
            
                if user_index < len(chat["ids"]):
                    return chat["ids"][user_index]  
                else:
                    return -1 
            else:
                return -1  
        
        except Exception as e:
            print(f"Error fetching chat for user_id {user_id}: {e}")
            return -1  

    def add_message(self, chat_id, message_type, message, sender_id):
        chat = self.chats_collection.find_one({"ids": chat_id})
    
        if chat:
            chat_index = chat["ids"].index(chat_id)

            if message_type == "sent":
                update_query = {
                    "$push": { f"messages_sent.{chat_index}": message }
                }
            elif message_type == "received":
                update_query = {
                    "$push": { f"messages_received.{chat_index}": message}
                }

            result = self.chats_collection.update_one(
                {"ids": chat_id},  
                update_query
            )

            return result.modified_count > 0  

        return False  

    def add_new_chat(self, user_id):
        """Add a new chat entry for the user in the existing chat document."""
        
        chat = self.chats_collection.find_one({"user_ids": {"$ne": user_id}})

        if chat:
            chat["user_ids"].append(user_id)
            user_index = len(chat["user_ids"]) - 1 
            chat["ids"].append(max(chat["ids"]) + 1) 
            chat["messages_sent"].append([])
            chat["messages_received"].append([])

            self.chats_collection.update_one(
                {"_id": chat["_id"]}, 
                {"$set": {
                    "user_ids": chat["user_ids"],
                    "ids": chat["ids"],
                    "messages_sent": chat["messages_sent"],
                    "messages_received": chat["messages_received"],
                }}
            )

            return chat["ids"][-1]  
        else:
            return self.add_new_chat(user_id) 

