from django import forms
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render


from wallet.forms import SignupForm

def index(request):
    return render(request, 'wallet/index.html')

def signup(request):
	# https://docs.djangoproject.com/en/1.9/topics/forms/
    # http://www.tangowithdjango.com/book/chapters/login.html#creating-a-user-registration-view-and-template
	# http://stackoverflow.com/questions/8917185/in-django-when-i-call-user-objects-create-userusername-email-password-why

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SignupForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
			# process the data in form.cleaned_data as required

			#new_user = form.save()
			#new_user.set_password(new_user.set_password)
			#new_user.save()

            new_user = User.objects.create_user(
                username=form.cleaned_data['username'],  
                password=form.cleaned_data['password1'])
            new_user.save()

            #if new_user is not None:
            #    login(request, new_user)

            # redirect to a new URL:
            return HttpResponseRedirect('/wallet/')
            
    # if a GET (or any other method) we'll create a blank form
    else:
        form = SignupForm()

    return render(request, 'wallet/signup.html', {'form': form})

def login(request):
	return HttpResponse("This is the log in page")

def logout(request):
	return HttpResponse("This is the log out page")

def homepage(request):
	return HttpResponse("This is the home page - when logged in (eventually)")