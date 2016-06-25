from django.test import TestCase

from bank.models import Users


class UserTests(TestCase):
    """Users model tests."""

    def test_str(self):

        user = Users(
        	first_name='John', 
        	last_name='Smith', 
        	email='test@test.com'
        	)

        self.assertEquals(
            str(user),
            'John Smith test@test.com 20',
        )