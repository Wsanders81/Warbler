"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all() 

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser.id = 1234
        
        db.session.commit()
    def tearDown(self) -> None:
        return super().tearDown()
        db.session.rollback()
        
    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
        
    def test_messages_show(self): 
        with self.client as client: 
            
            m = Message(
                id = 2222, 
                text = "Another Test", 
                user_id = self.testuser.id
            )
            db.session.add(m)
            db.session.commit()
            
            resp = client.get(f"/messages/{m.id}")
            msg = Message.query.get(m.id)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(msg.text, str(resp.data))
    
    
    
    def test_logged_out_add_message(self): 
        with self.client as client: 
            resp = client.post("/messages/new", data={"text" : "Test"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            
    def test_destroy_message(self): 
        m_len = Message.query.all()
        
        test_user = User.signup(username="fake user", 
                                email="fake@gmail.com", 
                                password="password123", 
                                image_url=None)
        test_user.id = 8888
        
        m = Message(
                id = 2222, 
                text = "Another Test", 
                user_id = self.testuser.id
        )
        db.session.add_all([test_user, m])
        db.session.commit()
        
        with self.client as client: 
            with client.session_transaction() as session: 
                session[CURR_USER_KEY] = test_user.id
            resp = client.post('/messages/2222/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            m_final_len = Message.query.all()
            self.assertEqual(len(m_len), len(m_final_len))

    def test_unauthorized_destroy_message(self): 
        with self.client as client: 
            
            res = client.post(f"/messages/1234/delete", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized", str(res.data))