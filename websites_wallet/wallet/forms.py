from decimal import *

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

class GetCoinForm(forms.Form):
    # http://tutorial.djangogirls.org/en/django_forms/
    # https://docs.djangoproject.com/en/1.9/topics/forms/modelforms/
    coinnum = forms.DecimalField(label='Number of coins wanted', min_value=Decimal('0.01'))
    #error_messages = {
    #'coinnum': {'required': "You can't make zero coins"}
    #}



#    def is_valid(self):
#        
#        valid = super(GetCoinForm, self).is_valid()
#        print("1test and valid: " + str(valid))
#        if valid:
#            value = self.cleaned_data.get('coinnum')
#            print("2test")
#            print("value is: " + str(value))
#            print("self.user is : " + str(self.user))

#            if (self.user.profile.balance - value) < 0:
#                raise ValidationError(
#                    _('%(value)s makes balance negative.'),
#                    params={'value': value},
#                )
#            return True

#        return False