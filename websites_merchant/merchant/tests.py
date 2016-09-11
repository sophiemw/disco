from django.test import Client, TestCase

from merchant.models import Category, Items

class BankViewsTestCase(TestCase):
	"""Tests around views"""

	def test_homepage(self):
		"""Make sure the user can see the homepage"""
		c = Client()
		response = c.get('/merchant/')
		self.assertEqual(response.status_code, 302)

		response = c.get('/merchant/homepage/?category=')
		self.assertEqual(response.status_code, 200)


	def test_itemdetail_notexist(self):
		c = Client()
		response = c.get('/merchant/1/')
		self.assertEqual(response.status_code, 404)


	def test_itemdetail_exist(self):
		c = Category(tag="Book")
		c.save()
		i = Items(title="title", description="description", price=15)
		i.save()
		i.tags.add(c)

		c = Client()
		response = c.get('/merchant/1/')
		self.assertEqual(response.status_code, 200)


	def test_itembuy_notexist(self):
		c = Client()
		response = c.get('/merchant/1/buy/')
		self.assertEqual(response.status_code, 404)


	def test_itembuy_exist(self):
		c = Category(tag="Book")
		c.save()
		i = Items(title="title", description="description", price=15)
		i.save()
		i.tags.add(c)

		c = Client()
		response = c.get('/merchant/1/buy/')
		self.assertEqual(response.status_code, 200)


	def test_itemsuccess_notexist(self):
		c = Client()
		response = c.get('/merchant/success2/1/')
		self.assertEqual(response.status_code, 404)


	def test_itemsuccess_exist(self):
		c = Category(tag="Book")
		c.save()
		i = Items(title="title", description="description", price=15)
		i.save()
		i.tags.add(c)

		c = Client()
		response = c.get('/merchant/success2/1/')
		self.assertEqual(response.status_code, 200)