from django.contrib.auth.models import User
from django.test import Client, TestCase

from bank.forms import RegisterForm
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

        ##profile = UserProfile.objects.get(user=TEST_USER['username'])
        u = User.objects.get(username=TEST_USER['username'])

        #profile = UserProfile.objects.get(user_id=u.id)
        #p = request.User.profile
        p = UserProfile(user=u, balance=TEST_USER['balance'])

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


    def test_unsuccessful_login(self):
        """Test that a user needs to have an existing account"""
        did_login_succeed = self.client.login(
            username='dummyusername',
            password=TEST_USER['password'])

        self.assertFalse(did_login_succeed)


    def test_new_user(self):
        """Test creating a user has default balance of 20"""
        c = Client()
        c.post('/bank/register/', {
            "username": "usernam2e",
            "password1": "johnpassword",
            "password2": "johnpassword",
            "email": "test@test.com",
            "first_name": "John",
            "last_name": "Smith"
            })

        u = User.objects.get(username='usernam2e')

        self.assertEquals(20, u.profile.balance)

    def test_new_user_different_password(self):
        """Test user creation if bad passwords"""
        form = RegisterForm({
            "username": "usernam2e",
            "password1": "johnpassword",
            "password2": "johnpassword2",
            "email": "test@test.com",
            "first_name": "John",
            "last_name": "Smith"
            })
        self.assertFalse(form.is_valid())


    def test_empty_registerform(self):
        """Test user creation if empty form"""
        form = RegisterForm({})
        self.assertFalse(form.is_valid())


class CoinCreationTests(TestCase):
    """Tests around coin creation"""

    def test_make_coins_not_enough_money(self):
        """Testing to make sure that a client cannot create more coins than they have money"""
        c = Client()
        c.post('/bank/register/', {
            "username": "usernam2e",
            "password1": "johnpassword",
            "password2": "johnpassword",
            "email": "test@test.com",
            "first_name": "John",
            "last_name": "Smith"
            })
        response = c.get('/bank/confirmcoincreation/21/')

        self.assertEquals(str(response.content), "Bank: Cannot create coins - insufficient funds")


    def test_make_coins_enough_money(self):
        """Testing to make sure that a client cannot create more coins than they have money"""
        c = Client()
        c.post('/bank/register/', {
            "username": "usernam2e",
            "password1": "johnpassword",
            "password2": "johnpassword",
            "email": "test@test.com",
            "first_name": "John",
            "last_name": "Smith"
            })
        response = c.get('/bank/confirmcoincreation/1/')

        self.assertEqual(response.status_code, 302)


    def test_coincreation_login(self):
        c = Client()
        c.post('/bank/register/', {
            "username": "username2",
            "password1": "johnpassword",
            "password2": "johnpassword",
            "email": "test@test.com",
            "first_name": "John",
            "last_name": "Smith"
            })
        self.assertTrue(c.login(username='username2', password='johnpassword'))

        response = c.get('/bank/coincreation/5/')

        self.assertEqual(response.status_code, 200)


class BankViewsTestCase(TestCase):
    """Tests around views"""

    def test_homepage_not_login(self):
        """If a user is not logged in they cannot see the homepage"""
        response = self.client.get('/bank/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/bank/login/?next=/bank/")


    def test_homepage_login(self):
        """If a user is logged in they can see the homepage"""
        
        c = Client()
        c.post('/bank/register/', {
            "username": "username1",
            "password1": "johnpassword",
            "password2": "johnpassword",
            "email": "test@test.com",
            "first_name": "John",
            "last_name": "Smith"
            })
        resp = c.get('/bank/')
        self.assertEqual(resp.status_code, 200)
#        self.assertTrue(c.login(username='username1', password='johnpassword'))

        #http://stackoverflow.com/questions/5660952/test-that-user-was-logged-in-successfully/35871564#35871564
        # djangos login function logs the user in
        self.assertIn('_auth_user_id', c.session)



    def test_register(self):
        resp = self.client.get('/bank/register/')
        self.assertEqual(resp.status_code, 200)


    def test_logout(self):
        c = Client()
        c.post('/bank/register/', {
            "username": "username2",
            "password1": "johnpassword",
            "password2": "johnpassword",
            "email": "test@test.com",
            "first_name": "John",
            "last_name": "Smith"
            })

        resp = c.get('/bank/')
        self.assertEqual(resp.status_code, 200)

 #       print (c.session['_auth_user_id'])
        response = c.get('/bank/logout/')
        self.assertNotIn('_auth_user_id', c.session)
#        print c.session['_auth_user_id']

        self.assertEqual(response.status_code, 302)
#        self.assertEqual(c.session['_auth_user_id'], [])
#        self.assertFalse(c.login(username='username2', password='johnpassword'))


    def test_login_form_good(self):
        c = Client()
        c.post('/bank/register/', {
            "username": "username2",
            "password1": "johnpassword",
            "password2": "johnpassword",
            "email": "test@test.com",
            "first_name": "John",
            "last_name": "Smith"
            })

        response = c.post('/bank/login/', {
            "username": "username2",
            "password": "johnpassword",
            })

        # http://stackoverflow.com/questions/5660952/test-that-user-was-logged-in-successfully/35871564#35871564
        #self.assertTrue(response.context['request'].user.is_authenticated())

        self.assertTrue(c.login(username='username2', password='johnpassword'))

    def test_login_form_good_redirect(self):
        c = Client()
        c.post('/bank/register/', {
            "username": "username2",
            "password1": "johnpassword",
            "password2": "johnpassword",
            "email": "test@test.com",
            "first_name": "John",
            "last_name": "Smith"
            })

        response = c.post('/bank/login/?next=/bank/homepage/', {
            "username": "username2",
            "password": "johnpassword",
            })

        self.assertEqual(response.status_code, 302)


    def test_login_form_bad(self):

        c = Client()
        c.post('/bank/register/', {
            "username": "username2",
            "password1": "johnpassword",
            "password2": "johnpassword",
            "email": "test@test.com",
            "first_name": "John",
            "last_name": "Smith"
            })

        response = c.post('/bank/login/', {
            "username": "username2",
            "password": "johnpassword2",
            })
        self.assertFalse(c.login(username='username1', password='johnpassword2'))


