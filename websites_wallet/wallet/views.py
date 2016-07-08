from django import forms
from django.contrib import auth
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext

from wallet.forms import GetCoinForm, SignupForm
from wallet.models import Coins

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

            new_user = User.objects.create_user(
                username=form.cleaned_data['username'],  
                password=form.cleaned_data['password1'])
            new_user.save()

            if new_user is not None:
                login(request, new_user)

            # redirect to a new URL:
            return HttpResponseRedirect('/wallet/')
            
    # if a GET (or any other method) we'll create a blank form
    else:
        form = SignupForm()

    return render(request, 'wallet/signup.html', {'form': form})

def userlogin(request):
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
                if next == "":
                    return HttpResponseRedirect('/wallet/')
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
        return render(request, 'wallet/login.html', {'next':next})

@login_required
def userlogout(request):
	logout(request)
	return HttpResponseRedirect('/wallet/')

@login_required
def homepage(request):
    # http://stackoverflow.com/questions/17754295/can-i-have-a-django-form-without-model
    
    if request.method == 'POST':
        form = GetCoinForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            coinnum = cd.get('coinnum')

            return render(request, 'wallet/gettingcoins.html', {'coinnum':coinnum})
    else:
        form = GetCoinForm()

    print(request.user)
    users_coins = Coins.objects.filter(user=request.user)
    #print(users_coins)
    context = {
        'form': form,
        'users_coins': users_coins
    }
    return render(request, 'wallet/homepage.html', context)

@login_required
def coinsuccess(request, coinnum):
    print("!!request.user: " + str(request.user))
    new_coin = Coins(user=request.user, value_of_coin=coinnum, coin_code="testcode")
    new_coin.save()

    context = {'coinnum': coinnum}
    return render(request, 'wallet/coinsuccess.html', context)


@login_required
def payment(request, user_getting_money, payment_amount, item_id):
    user_getting_money = get_object_or_404(User, username=user_getting_money)
    return render(request, 'wallet/payment.html', {'user_getting_money':user_getting_money, 'payment_amount':payment_amount, 'item_id':item_id})