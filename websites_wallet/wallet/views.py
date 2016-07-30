from django import forms
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext

from wallet.forms import GetCoinForm, SignupForm
from wallet.models import PaymentSession, Coins

import BLcred, blshim

import requests, datetime


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

            context = {
                'coinnum': cd.get('coinnum'),
                'BANK_URL': settings.BANK_URL
            }

            return render(request, 'wallet/gettingcoins.html', context)
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
def coinsuccess(request):
    num_of_coins, sessionid = blshim.deserialise(request.GET.get('entry'))

    valid = testcoincreation(request, num_of_coins, sessionid, request.user)

    if valid: 
        return render(request, 'wallet/coinsuccess.html', {'num_of_coins': num_of_coins})
    else:
        return HttpResponse("pi proof failed")


@login_required
def coinsuccess2(request):
    return render(request, 'wallet/coinsuccess2.html')


@login_required
def payment(request, payment_amount, item_id):
    sessionid = request.session._session_key

    # if sessionid exists already in the db, delete it
    try:
        test = PaymentSession.objects.get(sessionID=sessionid)
        test.delete()
    except PaymentSession.DoesNotExist:
        pass

    # create a session db to record information about the sale for the validation later
    p = PaymentSession(sessionID=sessionid, user=request.user, amount=payment_amount)
    p.save()

    context = {
        'payment_amount':payment_amount, 
        'item_id':item_id,
        'serialised_entry': blshim.serialise((item_id, sessionid)),
        'MERCHANT_URL': settings.MERCHANT_URL
    }
    return render(request, 'wallet/payment.html', context)


@login_required
def convertingcoinsbacktomoney(request, coinnum, coinpk):
    context = {
        'coinnum': coinnum,
        'BANK_URL': settings.BANK_URL,
        'coinpk': coinpk
    }
    return render(request, 'wallet/convertingcoinsbacktomoney.html', context)


@login_required
def coindestroysuccess(request, num_of_coins, coinpk):
    # TODO NEED TO CHANGE THIS TO SOMETHING UNIQUE
    request.user.coins_set.filter(pk=coinpk).delete()
    context = {'num_of_coins': num_of_coins}
    return render(request, 'wallet/coindestroysuccess.html', context)


@login_required
def coindestroysuccess2(request, num_of_coins):
    context = {'num_of_coins': num_of_coins}
    return render(request, 'wallet/coindestroysuccess2.html', context)


def testcoincreation(request, coinnum, sessionid, user):
    # http://www.saltycrane.com/blog/2008/06/how-to-get-current-date-and-time-in/
    now = datetime.datetime.now() 
    expirydate = now.year + 2

    if user.username == "expiredspender":
        expirydate = now.year - 2

    # value, expiry date
    LT_user_state, user_commit = BLcred.BL_user_setup(blshim.params, [coinnum, expirydate])

    (C, ) = user_commit
    pi_proof_values = blshim.pi_proof_wallet(C, LT_user_state.R, coinnum, expirydate)

    s_entry = blshim.serialise((pi_proof_values, user_commit, sessionid, coinnum, expirydate))

    r = requests.get(settings.BANK_URL + '/testPrepVal/?serialised_entry=%s' %(s_entry))
    c = r.content

    (valid, results) = blshim.deserialise(c)

    if valid:
        rnd, aap = results

        BLcred.BL_user_preparation(LT_user_state, rnd)

        msg_to_issuer_e = epsilon = BLcred.BL_user_validation(LT_user_state, (blshim.y, ), aap)

        # new webservice here
        # sending e
        s_entry = blshim.serialise((msg_to_issuer_e, user_commit, sessionid))
        
        r = requests.get(settings.BANK_URL + '/testVal2/?serialised_entry=%s' %(s_entry))
        c = r.content

        msg_to_user_crcprp = blshim.deserialise(c)

        signature = BLcred.BL_user_validation2(LT_user_state, msg_to_user_crcprp)

        ##VALIDATION THAT THE COIN IS VALID
        b = BLcred.BL_check_signature(blshim.params, (blshim.y, ), signature)

        # Saving the coin into the DB
        # signature and coins are different - mu
        # serialising the stuff to save in the db
        (m, LT_user_state.zet, LT_user_state.zet1, LT_user_state.zet2, om, omp, ro, ro1p, ro2p, mu) = signature

        coin = (m, LT_user_state.zet, 
                    LT_user_state.zet1, 
                    LT_user_state.zet2, om, omp, ro, ro1p, ro2p)

        serialised_code_rnd_tau_gam_R_att = blshim.serialise((coin, rnd, LT_user_state.tau, LT_user_state.gam, LT_user_state.R, LT_user_state.attributes))

        c = Coins(user=user, value_of_coin=coinnum, serialised_code_rnd_tau_gam_R_att=serialised_code_rnd_tau_gam_R_att, expirydate=expirydate)
        c.save()

    return valid 


def testspending(request):
    error = False
    error_reason = ""
    msg_to_merchant_epmupcoin = [""]
    serialised_entry = request.GET.get('entry')
    desc, sessionid, im = blshim.deserialise(serialised_entry)

    ps = PaymentSession.objects.get(sessionID=sessionid)
    amount = ps.amount
    user = ps.user

    # TODO make this easier to test
    list_of_coins = Coins.objects.filter(user=user).order_by('-value_of_coin')

    total_value = 0
    list_of_suitable_coins = []
    for c in list_of_coins:
        total_value += c.value_of_coin

    if total_value < amount:
        error = True
        error_reason = "not enough coins to buy item"
        print(error_reason)
    if not error:
        amount_remaining = amount
        for c in list_of_coins:
            if c.value_of_coin <= amount_remaining:
                amount_remaining -= c.value_of_coin
                list_of_suitable_coins.append(c)

        if amount_remaining == 0:
            print("GOOD AMOUNT OF COINS")
            print("coins: "+ str(list_of_suitable_coins))
        else: 
            error = True
            error_reason = "Wrong denominations of coins"
            print("FAIL")

    # user should actually be sent with the webservice (cheating here)
    # this is where the magic would happen with bundling up the coins to spend them
    
    list_of_msgs = []
    if not error:
        # for each coin, deserialise and run spending 2
        # put result into a list of messages      
        for c in list_of_suitable_coins:
            if user.username == "wrongvaluespender":
                c.value_of_coin += 1

            code_rnd_tau_gam_R_att = c.serialised_code_rnd_tau_gam_R_att
            coin, rnd, tau, gam, R, att = blshim.deserialise(code_rnd_tau_gam_R_att)
            # run spending_2 on each coin
            msg_to_merchant_epmupcoin = blshim.spending_2(tau, gam, coin, desc)

            (m, zet, zet1, zet2, om, omp, ro, ro1p, ro2p) = coin

            # table 8, revealing attributes for each coin
            # first check each coin is the value it says it is
            amount_rev_values = blshim.rev_attribute_1("amount", gam, zet, zet1, rnd, R, att)

            # now check the coin is within its expiry date
            expiry_rev_values = blshim.rev_attribute_1("expirydate", gam, zet, zet1, rnd, R, att)

            list_of_msgs.append((msg_to_merchant_epmupcoin, amount_rev_values, expiry_rev_values, c.value_of_coin, c.expirydate))

        if user.username != "doublespender":
            for c in list_of_suitable_coins:
                c.delete()
    # need to delete the session otherwise ps will return multiple objects
    ps.delete()
    # return all signed coins at once        
    return HttpResponse(blshim.serialise((not error, error_reason, list_of_msgs)))