from django.test import TestCase

#from bank.models import User
from django.contrib.auth.models import User
from bank.models import UserProfile

TEST_USER = {"username": "username",
            "password": "johnpassword",
            "email": "test@test.com",
            "first_name": "John",
            "last_name": "Smith",
            "balance":32
            }

class UserTests(TestCase):
    """Users model tests."""

    def setUp(self):
        """Insert demo users"""
        #create_user(username, email=None, password=None, **extra_fields)
        user = User.objects.create_user(
            username=TEST_USER['username'], 
            email=TEST_USER['email'], 
            password=TEST_USER['password'], 
            first_name=TEST_USER['first_name'], 
            last_name=TEST_USER['last_name'],
            #balance=TEST_USER['balance']
            )
        profile = UserProfile(user_id=user.id, balance=TEST_USER['balance'])
        profile.save()

    def test_create_user(self):
        """Test to check that creating a user does as expected"""
        #user = User(
        #    username='test',
        # 	first_name='John', 
        # 	last_name='Smith', 
        # 	email='test@test.com'
        # 	)

        print("TEST_USER= " + str(TEST_USER))

        ##profile = UserProfile.objects.get(user=TEST_USER['username'])
        u = User.objects.get(username=TEST_USER['username'])
        print("U is: " + str(u))

        #profile = UserProfile.objects.get(user_id=u.id)
        #p = request.User.profile
        p = UserProfile(user=u, balance=32)

        #print("P is : " + str(p))

        self.assertEquals(
            str(p),
            'username John Smith test@test.com 32',
        )


    def test_login(self):
        """Test that a user can log in successfully"""
        # http://stackoverflow.com/questions/26306424/cant-login-a-just-created-user-in-a-django-test
        did_login_succeed = self.client.login(
            username=TEST_USER['username'],
            password=TEST_USER['password'])

        self.assertTrue(did_login_succeed)