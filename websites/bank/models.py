from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# http://stackoverflow.com/questions/6085025/django-user-profile
# http://stackoverflow.com/questions/26306424/cant-login-a-just-created-user-in-a-django-test
@python_2_unicode_compatible  # only if you need to support Python 2
class UserProfile(models.Model):  
    user = models.OneToOneField(User, related_name='profile')
    balance = models.IntegerField(default=20)

    def __str__(self):
        return ' '.join([
			str(self.user.username),
    		str(self.user.first_name),
    		str(self.user.last_name),
    		str(self.user.email),
    		str(self.balance)
		])

    def __unicode__(self):
        return ' '.join([
            str(self.user.username),
            str(self.user.first_name),
            str(self.user.last_name),
            str(self.user.email),
            str(self.balance)
        ])