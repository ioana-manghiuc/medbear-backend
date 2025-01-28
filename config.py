import os
from dotenv_vault import load_dotenv

load_dotenv()

class Config:
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    MONGO_URI = os.getenv('MONGO_URI')
    DB_NAME = os.getenv('DB_NAME')
    SECRET_KEY = os.getenv('SECRET_KEY')
    FRONT_END_URL = os.getenv('FRONTEND_URL')