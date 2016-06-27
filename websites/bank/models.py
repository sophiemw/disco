from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

#@python_2_unicode_compatible  # only if you need to support Python 2
#class Users(models.Model):
#    first_name = models.CharField(max_length=200)
#    last_name = models.CharField(max_length=200)
#    email = models.EmailField(unique=True)
#    password = models.CharField(max_length=200)
#    balance = models.IntegerField(default=20)

#    def __str__(self):
#    	return ' '.join([
#    		self.first_name,
#    		self.last_name,
#    		self.email,
#    		str(self.balance)
#		])

@python_2_unicode_compatible  # only if you need to support Python 2
# http://stackoverflow.com/questions/6085025/django-user-profile
class UserProfile(models.Model):  
    user = models.OneToOneField(User, related_name='profile')
    balance = models.IntegerField(default=20)

    def __str__(self):
        return u'Profile of user: %s' % self.user.username