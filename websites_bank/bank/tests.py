from decimal import *

from django.test import TestCase

#from bank.models import User
from django.contrib.auth.models import User

from bank.forms import GetCoinForm
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
        p = UserProfile(user=u, balance=TEST_USER['balance'])

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

class CoinCreationTests(TestCase):
    """Coin creation tests"""
    # http://toastdriven.com/blog/2011/apr/17/guide-to-testing-in-django-2/


    def setUp(self):
        #create_user(username, email=None, password=None, **extra_fields)
        self.user = User.objects.create_user(
            username=TEST_USER['username'], 
            email=TEST_USER['email'], 
            password=TEST_USER['password'], 
            first_name=TEST_USER['first_name'], 
            last_name=TEST_USER['last_name'],
            )
        profile = UserProfile(user_id=self.user.id, balance=TEST_USER['balance'])
        profile.save()

    def test_cannot_submit_with_no_coin(self):
        """User cannot convert 0 coins"""
        form = GetCoinForm({
            'coinnum': 0
        })
        self.assertFalse(form.is_valid())
        #self.assertEqual(
        #    form.errors['coinnum'],
        #    ["You can't make zero coins"]
        #)

    def test_cannot_submit_not_a_number(self):
        """User cannot convert an amount of coins which is not a number"""
        form = GetCoinForm({
            'coinnum': "asd"
        })
        self.assertFalse(form.is_valid())

#    def test_coin_less_than_balance(self):
#        """User must choose an amount of coins less than their balance"""
#        form = GetCoinForm({
#            'user': self.user.username,
#            'balance': self.user.profile.balance,
#            'coinnum': 1.00
#            })

#        print ("users balance is :" + str(self.user.profile.balance - Decimal(1.00)))

#        self.assertTrue(form.is_valid())


 #   def test_coin_greater_than_balance(self):
#        """User cannot create more coins than they have balance"""
        #u = User.objects.get(username=TEST_USER['username'])
        #p = UserProfile(user=u, balance=TEST_USER['balance'])
#        form = GetCoinForm({
#            'user': self.user.username,
#            'balance': self.user.profile.balance,
#            'coinnum': 50
#        })

#        print ("self.user: " + str(self.user.profile.balance))

        #cleanform = form.is_valid()
        #u = self.setUp
#        self.assertFalse(form.is_valid())
        #self.assertFalse(form.user.validate_balance_positive())


