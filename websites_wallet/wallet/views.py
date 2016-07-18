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

import BLcred, blshim

import requests

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

    #TODO WEBSERVICE CALL


    print("!!request.user: " + str(request.user))
    new_coin = Coins(user=request.user, value_of_coin=coinnum, coin_code="testcode")
    new_coin.save()

    context = {'coinnum': coinnum}
    return render(request, 'wallet/coinsuccess.html', context)


@login_required
def payment(request, user_getting_money, payment_amount, item_id):
    user_getting_money = get_object_or_404(User, username=user_getting_money)
    context = {
        'user_getting_money':user_getting_money, 
        'payment_amount':payment_amount, 
        'item_id':item_id
    }
    return render(request, 'wallet/payment.html', context)


@login_required
def convertingcoinsbacktomoney(request, coinnum):
    context = {'coinnum': coinnum}
    return render(request, 'wallet/convertingcoinsbacktomoney.html', context)


@login_required
def coindestroysuccess(request, num_of_coins):
    # NEED TO CHANGE THIS TO SOMETHING UNIQUE
    request.user.coins_set.filter(value_of_coin=num_of_coins).delete()
    context = {'num_of_coins': num_of_coins}
    return render(request, 'wallet/coindestroysuccess.html', context)


def testcoincreation(request):



    # value, expiry date
    LT_user_state, user_commit = BLcred.BL_user_setup(blshim.params, [10, 20])

#    print("user_commit: " + str(user_commit))

    s_user_commit = blshim.serialise(user_commit)

    r = requests.get('http://192.168.33.10:8090/bank/testPrepVal/?serialised_C=%s' %(s_user_commit))
    c = r.content
    #d = json.loads(c)

    (rnd, aap) = blshim.deserialise(c)
#    print("rnd: " + str(rnd))
#    print("aap: " + str(aap))

    BLcred.BL_user_preparation(LT_user_state, rnd)

    msg_to_issuer_e = epsilon = BLcred.BL_user_validation(LT_user_state, (blshim.LT_issuer_state.y, ), aap)


    # new webservice here
    # sending e
    s_msg_to_issuer_ec = blshim.serialise((msg_to_issuer_e, user_commit))
    
    r = requests.get('http://192.168.33.10:8090/bank/testVal2/?serialised_ec=%s' %(s_msg_to_issuer_ec))
    c = r.content

    msg_to_user_crcprp = blshim.deserialise(c)

    signature = BLcred.BL_user_validation2(LT_user_state, msg_to_user_crcprp)

    ##VALIDATION THAT THE COIN IS VALID
    b = BLcred.BL_check_signature(blshim.params, (blshim.LT_issuer_state.y, ), signature)

#    print ("{{{{{{{{{{{{{{{{{{{{ " + str(b))



    # Saving the coin into the DB
    # signature and coins are different - mu
    # serialising the stuff to save in the db
    (m, LT_user_state.zet, LT_user_state.zet1, LT_user_state.zet2, om, omp, ro, ro1p, ro2p, mu) = signature

    coin = (m, LT_user_state.zet, 
                LT_user_state.zet1, 
                LT_user_state.zet2, om, omp, ro, ro1p, ro2p)

    serialised_code_rnd_tau_gam = blshim.serialise((coin, rnd, LT_user_state.tau, LT_user_state.gam))

    # actual code that puts it into the db
    # TODO different user and coin amount

    # user=request.user
    testuser = User.objects.get(username="test1")
    c = Coins(user=testuser, value_of_coin=3, serialised_code_rnd_tau_gam=serialised_code_rnd_tau_gam)
    c.save()




    return HttpResponse("user_commit: " + str(user_commit))


def testspending(request):

    serialised_entry = request.GET.get('entry')
    desc = blshim.deserialise(serialised_entry)

    # user should actually be sent with the webservice (cheating here)
    # this is where the magic would happen with bundling up the coins to spend them
    coin_rnd_tau_gam_ser = '[["",{"EcPt:":"A85957R6GVGiMPITNsu0_QOVOFqYAK1psakSKNA="},{"EcPt:":"A_aJ7Xrf4HXgv1q4lu1ZGxQPmTT2XIvDLQ362qA="},{"EcPt:":"Am9mlKHHaLNF2Ls4-4cUkd6O-Ba5wQWnE4jLQlc="},{"Bn:":"ELuHkg9MIUCSg15w9KzW3RCICpStN8zpyH-N5g=="},{"Bn:":"ex2eGlRMom5CDpLV-8UuZSl74ZULqIFaRQxRhQ=="},{"Bn:":"QgvQxhdOpjoFzNN37CxR_2q4d7uaqpYWzaGxwg=="},{"Bn:":"HL7kiLdf4TC3Bxu6EfbzlGH6hDMp_pHD9-cg2A=="},{"Bn:":"m2iX8hh3vEepsFsf-6f69YVrbz7U3Oy-_3EFsQ=="}],[{"Bn:":"vRAZI0jyDBkGFPpRm4kHvqRyJ1IS5L27w3t0Rw=="}],{"Bn:":"idiRz_BcWp8vWBzBpTG21gF05VqFZZR9QQy44g=="},{"Bn:":"gS1AyHSOdoW48RQ3ZCOqxxDMAdbP35KUSA67Lw=="}]'
    coin, rnd, tau, gam = blshim.deserialise(coin_rnd_tau_gam_ser)
    # does this user have enough coins in db to buy item
    # run spending_2 on each coin
    # return all signed coins at once


    # tau, gam, coin, desc
    msg_to_merchant_epmupcoin = blshim.spending_2(tau, gam, coin, desc)


    return HttpResponse(blshim.serialise(msg_to_merchant_epmupcoin))