import mongomock
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Database.user_dao import UserDAO
from Logic.user_bl import UserBL

@pytest.fixture
def mock_db():
    """Fixture to set up a mock MongoDB."""
    client = mongomock.MongoClient()
    db = client['test_db']
    users_collection = db['users']
    users_collection.insert_one({
        "ids": [2, 4],
        "usernames": ["lola", "bobo"], 
        "emails": ["lola@lola.com","bobo@bobo.com"]
    })
    return users_collection

def test_get_messages_sent_with_mongomock(mock_db):
    user_dao = UserDAO()
    user_dao.users_collection = mock_db
    user_bl = UserBL()
    user_bl.dao=user_dao

    result = user_bl.get_id_by_username(username="lola")

    assert result == 2
