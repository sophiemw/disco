from django import forms            

class SignupForm(forms.Form):
    firstname = forms.CharField(required = True, label='Your firstname')
    lastname = forms.CharField(required = True)
    email = forms.EmailField(required = True)
    password1 = forms.CharField(required = True, widget=forms.PasswordInput)
    password2 = forms.CharField(required = True, widget=forms.PasswordInput)
