class Chat:
    def __init__(self, chat_id, user_ids, messages_sent, messages_received):
        self.chat_id = chat_id
        self.user_ids = user_ids
        self.messages_sent = messages_sent
        self.messages_received = messages_received

    def __repr__(self):
        return f"Chat(chat_id={self.chat_id}, user_ids={self.user_ids}, messages_sent={self.messages_sent}, messages_received={self.messages_received})"

    @classmethod
    def from_dict(cls, chat_data):
        """Converts a dictionary to a Chat object."""
        return cls(
            chat_id=chat_data.get("chat_id"),
            user_ids=chat_data.get("user_ids"),
            messages_sent=chat_data.get("messages_sent"),
            messages_received=chat_data.get("messages_received")
        )

    def to_dict(self):
        """Converts the Chat object to a dictionary."""
        return {
            "chat_id": self.chat_id,
            "user_ids": self.user_ids,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received
        }