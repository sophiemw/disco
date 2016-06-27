from django import forms 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm           

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
