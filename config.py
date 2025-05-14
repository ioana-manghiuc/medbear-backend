import os
from dotenv import load_dotenv

load_dotenv()

class SysConfig:
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING')
    DB_NAME = os.getenv('DB_NAME')
    SECRET_KEY = os.getenv('SECRET_KEY')
    FRONT_END_URL = os.getenv('FRONTEND_URL')
    OLLAMA_URL = os.getenv('OLLAMA_URL')
    MODEL_NAME = os.getenv('MODEL_NAME')