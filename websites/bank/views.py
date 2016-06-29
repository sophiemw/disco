from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext, loader
from django import forms

from bank.forms import GetCoinForm, SignupForm
from bank.models import UserProfile

def index(request):
	return render(request, 'bank/index.html')


def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/bank/2')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        # http://stackoverflow.com/questions/21498682/django-csrf-verification-failed-request-aborted-csrf-cookie-not-set
        return render(request, 'bank/login.html', {})


#def user_logout():
# http://www.tangowithdjango.com/book/chapters/login.html
# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/bank/')


def signup(request):
	# https://docs.djangoproject.com/en/1.9/topics/forms/
	# if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SignupForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
			# process the data in form.cleaned_data as required

			new_user = form.save()
			new_user.set_password(new_user.set_password)
			new_user.save()

			profile = UserProfile(user_id=new_user.id)
			profile.save()

			if new_user is not None:
				login(request, new_user)

			# redirect to a new URL:
			#return HttpResponseRedirect(reverse('bank:homepage', args=(1,)))
			return HttpResponseRedirect('/bank/')
            
    # if a GET (or any other method) we'll create a blank form
    else:
        form = SignupForm()

    return render(request, 'bank/signup.html', {'form': form})

@login_required
def homepage(request):
    #return render(request, 'bank/homepage.html')

    # https://docs.djangoproject.com/en/1.9/topics/forms/
    # http://stackoverflow.com/questions/7349865/django-using-modelform-to-edit-existing-database-entry
    instance = UserProfile.objects.get(user_id=request.user.id)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        print("test1")
        # create a form instance and populate it with data from the request:
        form = GetCoinForm(request.POST, instance=instance, user=request.user)
        print("test2")
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            print("test3")
#            if form.validate_balance_positive():
            print("test4")
            new_coin = form.save(commit=False)
            new_coin.user_id = request.user.id
            # https://docs.djangoproject.com/en/1.9/topics/forms/#field-data
            new_coin.balance = new_coin.balance - form.cleaned_data['coinnum']
            new_coin.save()

                #print form.cleaned_data['coinnum']

            # redirect to a new URL:
            #return HttpResponseRedirect(reverse('bank:homepage', args=(1,)))
            return HttpResponse("Coins created successfully")
#            else:
#                return HttpResponse("Balance becomes negative")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = GetCoinForm(instance=instance)

    return render(request, 'bank/homepage.html', {'form': form})


def userlist(request):
	user_list = Users.objects.all()
	context = {
		'user_list': user_list,
	}
	return render(request, 'bank/userlist.html', context)

