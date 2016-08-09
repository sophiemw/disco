from django.test import TestCase

# Create your tests here.
      # Ensure that non-existent polls throw a 404.
      resp = self.client.get('/polls/2/')
      self.assertEqual(resp.status_code, 404)