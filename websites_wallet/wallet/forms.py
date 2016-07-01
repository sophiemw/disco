from django import forms 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.template import RequestContext

# https://docs.djangoproject.com/en/1.9/ref/validators/

class SignupForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username',)