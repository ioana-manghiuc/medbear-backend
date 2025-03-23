from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
from Logic.user_bl import UserBL 
from Logic.chat_bl import ChatBL
from datetime import timedelta
from config import SysConfig
import uuid

user_service = UserBL()
chat_bl = ChatBL()

if __name__ == "__main__":
    print(chat_bl.get_user_chats(1))