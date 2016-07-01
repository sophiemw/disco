from django.test import TestCase

from django.contrib.auth.models import User

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

	def test_login(self):
		"""Test that a user can log in successfully"""
		# http://stackoverflow.com/questions/26306424/cant-login-a-just-created-user-in-a-django-test
		did_login_succeed = self.client.login(
			username=TEST_USER['username'],
			password=TEST_USER['password'])

		self.assertTrue(did_login_succeed)