from __future__ import unicode_literals

#from decimal import *

from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

# http://stackoverflow.com/questions/6085025/django-user-profile
# http://stackoverflow.com/questions/26306424/cant-login-a-just-created-user-in-a-django-test
# http://stackoverflow.com/questions/34578193/minvaluevalidator-not-working-on-decimalfield-in-django
@python_2_unicode_compatible  # only if you need to support Python 2
class UserProfile(models.Model):  
    user = models.OneToOneField(User, related_name='profile')
    balance = models.IntegerField(
        #decimal_places=2, 
        default=20, 
        #max_digits=12, 
        #validators=[validators.MinValueValidator(Decimal('0.01'))]
        validators=[validators.MinValueValidator(1)]
        )

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


@python_2_unicode_compatible  # only if you need to support Python 2
class CoinValidation(models.Model):
    commitment = models.TextField()
    jsonstring = models.TextField()
    sessionID = models.TextField()
    username = models.TextField()
    num_of_coins = models.IntegerField()

    def __str__(self):
        return self.commitment


@python_2_unicode_compatible  # only if you need to support Python 2
class DoubleSpendingz1Touser(models.Model):
    z1 = models.TextField()
    username = models.TextField()

    def __str__(self):
        return self.username + " " + self.z1 


@python_2_unicode_compatible  # only if you need to support Python 2
class DoubleSpendingCoinHistory(models.Model):
    coin = models.TextField()

    # epsilonp, mup
    serialised_entry = models.TextField()

    def __str__(self):
        return self.coin + "     " + self.serialised_entry