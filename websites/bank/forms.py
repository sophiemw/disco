from decimal import *

from django import forms 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.template import RequestContext


from bank.models import UserProfile     

class SignupForm(UserCreationForm):
    #http://stackoverflow.com/questions/16562529/django-1-5-usercreationform-custom-auth-model
    #password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    #password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

        def save(self, commit=True):
            user = super(UserCreateForm, self).save(commit=False)
            #user.email = self.cleaned_data["email"]
            if commit:
                user.save()
            return user

class GetCoinForm(forms.ModelForm):
    # http://tutorial.djangogirls.org/en/django_forms/
    # https://docs.djangoproject.com/en/1.9/topics/forms/modelforms/
    coinnum = forms.DecimalField(label='Number of coins wanted', min_value=Decimal('0.01'))
    #error_messages = {
    #'coinnum': {'required': "You can't make zero coins"}
    #}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        super(GetCoinForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserProfile
        #exclude = ['user', 'balance']
        #exclude = ['balance']

        fields = ['user', 'balance']

    def is_valid(self):
        
        valid = super(GetCoinForm, self).is_valid()
        print("1test and valid: " + str(valid))
        if valid:
            value = self.cleaned_data.get('coinnum')
            print("2test")
            print("value is: " + str(value))
            print("self.user is : " + str(self.user))

            if (self.user.profile.balance - value) < 0:
                raise ValidationError(
                    _('%(value)s makes balance negative.'),
                    params={'value': value},
                )
            return True

        return False





    # http://stackoverflow.com/questions/1202839/get-request-data-in-django-form
    # http://stackoverflow.com/questions/7299973/django-how-to-access-current-request-user-in-modelform/7300076#7300076
    def validate_balance_positive(self):
        value = self.cleaned_data.get('coinnum')
        if (self.user.profile.balance - value) < 0:
            raise ValidationError(
                _('%(value)s makes balance negative.'),
                params={'value': value},
            )
        return value