from decimal import *

from django.contrib import auth
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext, loader
from django import forms

from bank.forms import SignupForm
from bank.models import UserProfile

def index(request):
	return render(request, 'bank/index.html')


def user_login(request):
    # http://stackoverflow.com/questions/16750464/django-redirect-after-login-not-working-next-not-posting
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    next = ""
    if request.GET:  
#        print("!!!TEST: " + next)
        next = request.GET['next']
#        print("!!!TEST22: " + next)

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
                #return HttpResponseRedirect('/bank/')

#                print("!!!next: "+ next)
                if next == "":
                    return HttpResponseRedirect('/bank/')
                else:
                    return HttpResponseRedirect(next)

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
        return render(request, 'bank/login.html', {'next':next})



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
                email=form.cleaned_data['email'], 
                first_name=form.cleaned_data['first_name'], 
                last_name=form.cleaned_data['last_name'], 
                password=form.cleaned_data['password1'])
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
#    instance = UserProfile.objects.get(user_id=request.user.id)

    # if this is a POST request we need to process the form data
#    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
#        form = GetCoinForm(request.POST, instance=instance, user=request.user)
        # check whether it's valid:
#        if form.is_valid():
            # process the data in form.cleaned_data as required
 #            if form.validate_balance_positive():
#            new_coin = form.save(commit=False)
#            new_coin.user_id = request.user.id
            # https://docs.djangoproject.com/en/1.9/topics/forms/#field-data
#            new_coin.balance = new_coin.balance - form.cleaned_data['coinnum']
#            new_coin.save()

                #print form.cleaned_data['coinnum']

            # redirect to a new URL:
            #return HttpResponseRedirect(reverse('bank:homepage', args=(1,)))
#            return HttpResponse("Coins created successfully")
 #            else:
 #                return HttpResponse("Balance becomes negative")

    # if a GET (or any other method) we'll create a blank form
#    else:
#        form = GetCoinForm(instance=instance)

#    return render(request, 'bank/homepage.html', {'form': form})
    return render(request, 'bank/homepage.html')

def userlist(request):
	user_list = Users.objects.all()
	context = {
		'user_list': user_list,
	}
	return render(request, 'bank/userlist.html', context)

@login_required
def coincreation(request, num_of_coins):
    context = {
        'num_of_coins': num_of_coins,
    }
    return render(request, 'bank/coincreation.html', context)

@login_required
def confirmcoincreation(request, num_of_coins):
    print("!!request.user: " + str(request.user.profile.balance))
    if (Decimal(request.user.profile.balance) - Decimal(num_of_coins)) < 0:
        return HttpResponse("Bank: Cannot create coins - insufficient funds")
    else:
        request.user.profile.balance = Decimal(request.user.profile.balance) - Decimal(num_of_coins)
        request.user.profile.save()
        print("!!!!New balance: " + str(request.user.profile.balance))
        #return HttpResponse("Bank: Coins created successfully")
        return HttpResponseRedirect('http://192.168.33.10:8000/wallet/coinsuccess/' + num_of_coins)