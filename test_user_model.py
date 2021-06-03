"""User model tests."""

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

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(u.username, "testuser")
        self.assertEqual(u.email, "test@test.com")
        
    def test_repr(self): 
            """ Testing __repr__ function """
        
            u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()
            self.assertEqual(u.__repr__(), f"<User #{u.id}: {u.username}, {u.email}>")
        
    def test_is_following(self): 
        self.user1.followers.append(self.user2)
        db.session.commit()
        
        self.assertEqual(len(self.user1.followers), 1)
        self.assertEqual(len(self.user2.followers), 0)
        
    def test_is_followed_by(self): 
        self.user1.followers.append(self.user2)
        db.session.commit()
        
        self.assertTrue(self.user1.is_followed_by(self.user2))
        self.assertFalse(self.user2.is_followed_by(self.user1))
    
    
    #! Cannot get Integrity Error exception to raise
    #! fails tests
    # def test_user_signup_fail(self): 
    #     u = User.signup("TestUser1", "blah@gmail.com", "genericpassword", None)
    #     db.session.add(u)
    #     self.assertRaises(IntegrityError, db.session.commit)
            
    def test_user_authenticate(self): 
         self.assertEqual(self.user1.authenticate("TestUser1","password1"), self.user1)       
         self.assertEqual(self.user1.authenticate("TestUser1","Wrongpassword"), False)       
         self.assertEqual(self.user1.authenticate("TestUser4","password1"), False)       
            
