"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from sqlite3 import IntegrityError
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()




class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        
        self.client = app.test_client()


        #** Add test users 
        
        self.user1 = User.signup(
            username="TestUser1", 
            email = "Test1@email.com", 
            password = "password1", 
            image_url=""
        )
        self.user1.id = 1234
        
        self.user2 = User.signup(
            username="TestUser2", 
            email = "Test2@emailcom", 
            password="password2", 
            image_url=""
        )
        self.user2.id = 2345
        
        
        
        db.session.commit()
        
    def tearDown(self):
        """ Remove any fouled transactions """
        db.session.rollback()
        
    def test_message_model(self): 
        """Test message model / Adding message"""
        msg = Message(text="Test message for user 1", user_id=self.user1.id)
        db.session.add(msg)
        db.session.commit()
        self.assertEqual(len(self.user1.messages), 1)
        self.assertEqual(self.user1.messages[0].text, "Test message for user 1")

    def test_adding_messages(self): 
        """Test addition of new messages for users"""
        message = Message(text="Test message", user_id=self.user1.id)
        db.session.add(message)
        db.session.commit()
        
        self.assertIn(message, self.user1.messages)
        
    def test_message_deletion(self): 
        message = Message(text="Test message", user_id=self.user1.id)
        self.user1.messages.append(message)
        self.assertIn(message, self.user1.messages)

        self.user1.messages.remove(message)
        self.assertNotIn(message, self.user1.messages)

        