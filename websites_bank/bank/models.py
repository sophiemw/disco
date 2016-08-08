from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# http://stackoverflow.com/questions/6085025/django-user-profile
# http://stackoverflow.com/questions/26306424/cant-login-a-just-created-user-in-a-django-test
# http://stackoverflow.com/questions/34578193/minvaluevalidator-not-working-on-decimalfield-in-django
@python_2_unicode_compatible  # only if you need to support Python 2
class UserProfile(models.Model):  
    user = models.OneToOneField(User, related_name='profile')
    balance = models.IntegerField(
        default=20, 
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    num_of_coins = models.IntegerField()

    def __str__(self):
        return self.commitment


@python_2_unicode_compatible  # only if you need to support Python 2
class DoubleSpendingz1Touser(models.Model):
    z1 = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value_of_coin = models.IntegerField()
    expirydate = models.IntegerField()

    def __str__(self):
        return self.user.username + " " + self.z1 


@python_2_unicode_compatible  # only if you need to support Python 2
class DoubleSpendingCoinHistory(models.Model):
    coin = models.TextField()

    # epsilonp, mup
    serialised_entry = models.TextField()

    def __str__(self):
        return self.coin + "     " + self.serialised_entry


@python_2_unicode_compatible  # only if you need to support Python 2
class UsersWhoHaveDoubleSpent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)
    coin = models.TextField()

    # epsilonp, mup
    serialised_entry = models.TextField()

    def __str__(self):
        return ' '.join([
            self.user.username,
            str(self.time),
            self.coin
        ])