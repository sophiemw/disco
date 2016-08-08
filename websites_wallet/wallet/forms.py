from django import forms 
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.template import RequestContext

# https://docs.djangoproject.com/en/1.9/ref/validators/
# https://docs.djangoproject.com/en/dev/ref/forms/fields/#choicefield

class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username',)

class GetCoinForm(forms.Form):
    # http://tutorial.djangogirls.org/en/django_forms/
    # https://docs.djangoproject.com/en/1.9/topics/forms/modelforms/
    coinnum = forms.ChoiceField(label='Number of coins wanted:', choices=settings.COIN_VALUE_CHOICES)