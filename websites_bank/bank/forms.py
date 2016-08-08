from django import forms 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    # http://stackoverflow.com/questions/16562529/django-1-5-usercreationform-custom-auth-model
    # http://jessenoller.com/blog/2011/12/19/quick-example-of-extending-usercreationform-in-django
    # https://github.com/django/django/blob/master/django/contrib/auth/forms.py

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
