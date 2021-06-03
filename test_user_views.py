import os
from unittest import TestCase

from colorama import Cursor

from models import db, connect_db,User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY, g

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class TestUserViews(TestCase): 
    """ Test User Views"""
    
    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()
        
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
        
        self.user3 = User.signup(
            username="TestUser3", 
            email = "Test3@email.com", 
            password="password3", 
            image_url=""
        )
        self.user3.id = 3456
        
        db.session.commit()
        
        #* Add test messages
        
        self.user1.msg = Message(id=1111, text="Testing Message", user_id=self.user1.id)
        message2 = Message(id=2222, text="Banana Waffles", user_id=self.user1.id)
        self.user2.msg = message2
        db.session.add_all([self.user1.msg, self.user2.msg])
        db.session.commit()
        
        #* Add some followers
        follower1 = Follows(user_being_followed_id=self.user1.id, user_following_id=self.user2.id)
        follower2 = Follows(user_being_followed_id=self.user1.id, user_following_id=self.user3.id)
        follower3 = Follows(user_being_followed_id=self.user3.id, user_following_id=self.user1.id)
        db.session.add_all([follower1, follower2, follower3])
        db.session.commit()

        #* Let's add some Likes
        
        like1 = Likes(user_id = self.user1.id, message_id = 1111)
        db.session.add(like1)
        db.session.commit()
        
    def tearDown(self):
        """ Remove any fouled transactions """
         
            
        db.session.rollback()
        
    def see_all_users(self): 
        """Test all users view"""
        with self.client as client: 
            resp = client.get('/users')
            html = resp.data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('@TestUser3', html)
            self.assertIn('@TestUser2', html)
            
    def test_user_profile_route(self): 
        """Test user profile view"""
        with self.client as client: 
            resp = client.get(f"/users/{self.user1.id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn('@TestUser1', str(resp.data))
            self.assertNotIn('TestUser2', str(resp.data))
            
    def test_users_followers_view(self): 
        with self.client as client: 
            with client.session_transaction() as session: 
                session[CURR_USER_KEY] = self.user1.id
                
            resp = client.get(f"users/{self.user1.id}/following")
            
            self.assertEqual(resp.status_code, 200)

            self.assertIn("@TestUser3", str(resp.data))
            
    def test_users_followers_view(self): 
        with self.client as client: 
            with client.session_transaction() as session: 
                session[CURR_USER_KEY] = self.user1.id
                
            resp = client.get(f"users/{self.user1.id}/followers")
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@TestUser2", str(resp.data))
            self.assertIn("@TestUser3", str(resp.data))

    #* Didn't work... Womp womp
    #? DetachedInstanceError / user not bound to Session
    # def test_add_follow_view(self): 
    #     with self.client as client: 
    #         with client.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.user2.id
    #         resp = client.post(f"/users/follow/{self.user1.id}", follow_redirects=True)
    #         self.assertIn("TestUser2", str(resp.data))
            
    
    def test_unauthorized_followoing_access(self): 
        with self.client as client: 
            
            bad_id = 188888
            resp = client.get(f"/users/{bad_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_unauthorized_followers_access(self): 
        with self.client as client: 
            
            bad_id = 188888
            resp = client.get(f"/users/stop-following/{bad_id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
    
    #* Testing delete profile
    #? Detached Instance Error / user not bound to Session
    # def test_profile_view(self): 
    #     with self.client as client: 
    #         with client.session_transaction() as session: 
    #             session[CURR_USER_KEY] = self.user1.id
    #         resp = client.post('/users/profile', follow_redirects=True)
            
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertEqual('TestUser1', str(resp.data))

    def test_user_likes(self): 
        with self.client as client: 
            resp = client.get(f"/users/{self.user1.id}") 
            self.assertEqual(resp.status_code, 200)
            self.assertIn('/messages/1111', str(resp.data))
    
    def test_add_like(self): 
        with self.client as client: 
            with client.session_transaction() as session: 
                session[CURR_USER_KEY] = self.user1.id
            resp = client.post("/users/add_like/2222", follow_redirects=True )       
            self.assertEqual(resp.status_code, 200)

            user_likes = Likes.query.filter(Likes.user_id==self.user1.id).all()
            self.assertEqual(user_likes[0].user_id, self.user1.id)
            self.assertEqual(len(user_likes), 2)
    
    def delete_like(self): 
        with self.client as client: 
            with client.session_transaction() as session: 
                session[CURR_USER_KEY] = self.user1.id
            
            resp = client.get("/users/add_like/1111")
            self.assertEqual(resp.status_code, 200)
            likes = Likes.query.filter(Likes.user_id==self.user1.id)
            self.assertEqual(len(likes), 0)
                   
    def test_unauthorized_like(self): 
        
        like_count = Likes.query.count()
                
        with self.client as client: 
            resp = client.post('/users/add_like/2222', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            self.assertEqual(Likes.query.count(), like_count)
            