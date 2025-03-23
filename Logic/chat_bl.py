from Database.chat_dao import ChatDAO

class ChatBL:
    def __init__(self):
        self.dao = ChatDAO()

    def get_chat_by_user_id(self, user_id):
        """Fetch the chat associated with the given user_id."""
        chat = self.dao.find_chat_by_user_id(user_id)
        if chat:
            return chat.to_dict()  
        return {"message": "Chat not found"}
    
    def get_chat_id(self, user_id):
        """
        Fetch the chat associated with a user_id.
        If no chat exists, return None.
        """
        chat_id = self.dao.get_chat_by_user_id(user_id)
        if chat_id is not None:
            return chat_id
        else:
            return None
        
    def get_user_chats(self, user_id):
        """Fetch all chat IDs belonging to a user."""
        return self.dao.get_chats_by_user_id(user_id)


    def get_messages(self, chat_id):
        """Fetch both sent and received messages for a given chat_id."""
        messages_sent = self.dao.get_messages_sent(chat_id)
        messages_received = self.dao.get_messages_received(chat_id)

        if messages_sent is None and messages_received is None:
            return None  # Ensures a 404 is returned in `app.py`

        return {
            "messages_sent": messages_sent if messages_sent else [],
            "messages_received": messages_received if messages_received else []
        }

    
    def start_new_chat(self, user_id):
        """Start a new chat between users."""
        existing_chat = self.dao.find_chat_by_user_id(user_id)
        if existing_chat:
            return existing_chat
        chat_id = self.dao.add_new_chat(user_id)
        return chat_id

    def send_user_message(self, chat_id, message, sender_id):
        """Send a message in the chat."""
        if self.dao.add_user_message(chat_id, sender_id, message):
            return {"message": "Message sent successfully"}
        return {"message": "Failed to send message"}
    
    