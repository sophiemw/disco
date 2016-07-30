from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# https://docs.djangoproject.com/en/1.9/topics/db/examples/many_to_one/
@python_2_unicode_compatible  # only if you need to support Python 2
class Coins(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	value_of_coin = models.IntegerField(validators=[validators.MinValueValidator(0)])
	serialised_code_rnd_tau_gam_R_att = models.CharField(max_length=500, )
	expirydate = models.IntegerField()

	def __str__(self):
		return ' '.join([
			str(self.user.username),
			str(self.value_of_coin)
		])


@python_2_unicode_compatible  # only if you need to support Python 2
class PaymentSession(models.Model):
	sessionID = models.TextField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	amount = models.IntegerField()

	def __str__(self):
		return self.user.username + " " + str(self.amount)
