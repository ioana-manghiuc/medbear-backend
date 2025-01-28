import mongomock
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Database.chat_dao import ChatDAO

@pytest.fixture
def mock_db():
    """Fixture to set up a mock MongoDB."""
    client = mongomock.MongoClient()
    db = client['test_db']
    chats_collection = db['chats']
    chats_collection.insert_one({
        "ids": [1, 2],
        "user_ids": [2, 3], 
        "messages_sent": [
            ["hi", "hello"],  
            ["foo", "bar"],   
        ]
    })
    return chats_collection


def test_get_messages_sent_with_mongomock(mock_db):
    chat_dao = ChatDAO()
    chat_dao.chats_collection = mock_db

    result = chat_dao.get_messages_sent(chat_id=2)

    assert result == ["foo", "bar"]
    
def test_get_chat_by_user_id_with_mongomock(mock_db):
    chat_dao = ChatDAO()
    chat_dao.chats_collection = mock_db
    result = chat_dao.get_chat_by_user_id(user_id=3)

    assert result == 2
    
def test_add_message_with_mongomock(mock_db):
    chat_dao = ChatDAO()  
    chat_dao.chats_collection = mock_db  
    result = chat_dao.add_message(chat_id=1, message_type="sent", message="test message", sender_id=2)
    updated_chat = chat_dao.chats_collection.find_one({"ids": 1})
    assert result is True
    assert updated_chat["messages_sent"][0] == ["hi", "hello", "test message"]