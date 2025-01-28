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

    def get_messages(self, chat_id):
        """Fetch only the messages_sent for a given chat_id."""
        messages = self.dao.get_messages_sent(chat_id) 
        if messages:
            return {"messages_sent": messages}  
        return {"message": "Chat not found"} 
    
    def start_new_chat(self, user_id):
        """Start a new chat between users."""
        existing_chat = self.dao.find_chat_by_user_id(user_id)
        if existing_chat:
            return existing_chat
        chat_id = self.dao.add_new_chat(user_id)
        return chat_id

    def send_message(self, chat_id, message, sender_id):
        """Send a message in the chat."""
        if self.dao.add_message(chat_id, "sent", message, sender_id):
            return {"message": "Message sent successfully"}
        return {"message": "Failed to send message"}

    def receive_message(self, chat_id, message, sender_id):
        """Receive a message in the chat."""
        if self.dao.add_message(chat_id, "received", message, sender_id):
            return {"message": "Message received successfully"}
        return {"message": "Failed to receive message"}