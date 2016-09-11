from django.test import Client, TestCase

from django.contrib.auth.models import User

from wallet.forms import GetCoinForm, RegisterForm
from wallet.models import PaymentSession, Coins

TEST_USER = {"username": "testusername",
			"password": "testpassword",
			}

class UserTests(TestCase):
	"""Users model tests."""
	def setUp(self):
		"""Insert demo users"""
		#create_user(username, email=None, password=None, **extra_fields)
		user = User.objects.create_user(
		username=TEST_USER['username'], 
		password=TEST_USER['password'], 
		)


	def test_succuessful_login(self):
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


class WalletViewsTestCase(TestCase):
	"""Testing the wallet's views."""

	def test_homepage_not_login(self):
		"""If a user is not logged in they cannot see the homepage"""
		response = self.client.get('/wallet/')
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, "/wallet/login/?next=/wallet/")


	def test_homepage_login(self):
		"""If a user is logged in they can see the homepage"""

		c = Client()
		c.post('/wallet/register/', {
			"username": "username1",
			"password1": "johnpassword",
			"password2": "johnpassword",
			"email": "test@test.com",
			"first_name": "John",
			"last_name": "Smith"
		})
		resp = c.get('/wallet/')
		self.assertEqual(resp.status_code, 200)

		#http://stackoverflow.com/questions/5660952/test-that-user-was-logged-in-successfully/35871564#35871564
		# djangos login function logs the user in
		self.assertIn('_auth_user_id', c.session)


	def test_register(self):
		resp = self.client.get('/wallet/register/')
		self.assertEqual(resp.status_code, 200)


	def test_logout(self):
		c = Client()
		c.post('/wallet/register/', {
			"username": "username2",
			"password1": "johnpassword",
			"password2": "johnpassword",
			"email": "test@test.com",
			"first_name": "John",
			"last_name": "Smith"
		})

		resp = c.get('/wallet/')
		self.assertEqual(resp.status_code, 200)

		response = c.get('/wallet/logout/')
		self.assertNotIn('_auth_user_id', c.session)

		self.assertEqual(response.status_code, 302)


	def test_login_form_good(self):
		c = Client()
		c.post('/wallet/register/', {
			"username": "username2",
			"password1": "johnpassword",
			"password2": "johnpassword",
			"email": "test@test.com",
			"first_name": "John",
			"last_name": "Smith"
		})

		response = c.post('/wallet/login/', {
		"username": "username2",
		"password": "johnpassword",
		})

		# http://stackoverflow.com/questions/5660952/test-that-user-was-logged-in-successfully/35871564#35871564
		self.assertTrue(c.login(username='username2', password='johnpassword'))


	def test_login_form_good_redirect(self):
		c = Client()
		c.post('/wallet/register/', {
			"username": "username2",
			"password1": "johnpassword",
			"password2": "johnpassword",
			"email": "test@test.com",
			"first_name": "John",
			"last_name": "Smith"
		})

		response = c.post('/wallet/login/?next=/bank/homepage/', {
		"username": "username2",
		"password": "johnpassword",
		})

		self.assertEqual(response.status_code, 302)


	def test_login_form_bad(self):
		c = Client()
		c.post('/wallet/register/', {
			"username": "username2",
			"password1": "johnpassword",
			"password2": "johnpassword",
			"email": "test@test.com",
			"first_name": "John",
			"last_name": "Smith"
		})

		response = c.post('/wallet/login/', {
		"username": "username2",
		"password": "johnpassword2",
		})
		self.assertFalse(c.login(username='username1', password='johnpassword2'))


class CreateCoinsTest(TestCase):
	def test_create_coin(self):
		c = Client()
		c.post('/wallet/register/', {
			"username": "username2",
			"password1": "johnpassword",
			"password2": "johnpassword",
			"email": "test@test.com",
			"first_name": "John",
			"last_name": "Smith"
		})

		response = c.post('/wallet/', {'coinnum': 1})
		self.assertEqual(response.status_code, 200)


	def test_create_coin_form(self):
		form = GetCoinForm({'coinnum': 5})
		self.assertTrue(form.is_valid())


	def test_create_coin_form_notvalid(self):
		form = GetCoinForm({'coinnum': 6})
		self.assertFalse(form.is_valid())


	def test_coinsuccess2(self):
		c = Client()
		c.post('/wallet/register/', {
			"username": "username2",
			"password1": "johnpassword",
			"password2": "johnpassword",
			"email": "test@test.com",
			"first_name": "John",
			"last_name": "Smith"
		})
		response = c.get('/wallet/coinsuccess2/')
		self.assertEqual(response.status_code, 200)


	def test_paymentpage_login(self):
		c = Client()
		c.post('/wallet/register/', {
			"username": "username2",
			"password1": "johnpassword",
			"password2": "johnpassword",
			"email": "test@test.com",
			"first_name": "John",
			"last_name": "Smith"
		})
		response = c.get('/wallet/1/1/')
		self.assertEqual(response.status_code, 200)


	def test_paymentpage_logout(self):
		c = Client()
		response = c.get('/wallet/1/1/', follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.redirect_chain, [('/wallet/login/?next=/wallet/1/1/', 302)])



	def test_coindestroysuccess2(self):
		c = Client()

		c.post('/wallet/register/', {
			"username": "username2",
			"password1": "johnpassword",
			"password2": "johnpassword",
			"email": "test@test.com",
			"first_name": "John",
			"last_name": "Smith"
		})

		response = c.get('/wallet/coindestroysuccess2/1/')
		self.assertEqual(response.status_code, 200)
