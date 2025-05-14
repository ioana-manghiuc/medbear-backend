class UserModel:
    def __init__(self, user_id, username, email, password=None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f"User(id={self.user_id}, username={self.username}, email={self.email})"

    @classmethod
    def from_dict(cls, user_data):
        """Converts a dictionary to a User object."""
        return cls(
            user_id=user_data.get("id"),
            username=user_data.get("username"),
            email=user_data.get("email"),
            password=user_data.get("password"),
        )

    def to_dict(self):
        """Converts the User object to a dictionary."""
        return {
            "id": self.user_id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
        }