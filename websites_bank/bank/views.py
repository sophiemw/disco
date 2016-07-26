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
from bank.models import DoubleSpendingCoinHistory, DoubleSpendingz1Touser, CoinValidation, UserProfile

import blshim, BLcred

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
    new_balance = int(request.user.profile.balance) - int(num_of_coins)

    if (new_balance) < 0:
        return HttpResponse("Bank: Cannot create coins - insufficient funds")
    else:
        sessionid = request.session._session_key

        # Remove any old entries that might have been created by defects
        db = CoinValidation.objects.filter(sessionID=sessionid)
        db.delete()

        j = CoinValidation(sessionID=sessionid, username=request.user.username, num_of_coins=num_of_coins, commitment="", jsonstring="")
        j.save()
        
        entry = blshim.serialise((int(num_of_coins), sessionid))

        s = 'http://192.168.33.10:8000/wallet/coinsuccess/?entry=%s' %(entry)

        return HttpResponseRedirect(s)

@login_required
def coindestroy(request, num_of_coins):
    print("!!request.user: " + str(request.user.profile.balance))
    context = {
        'num_of_coins': num_of_coins
    }
    return render(request, 'bank/coindestroy.html', context)


@login_required
def coindestroysuccess(request, num_of_coins):
    context = {'num_of_coins': num_of_coins}
    print("!!request.user before: " + str(request.user.profile.balance))
    request.user.profile.balance = request.user.profile.balance + int(num_of_coins)
    request.user.profile.save()
    print("!!request.user after: " + str(request.user.profile.balance))
    #return render(request, 'bank/coindestroysuccess.html', context)
    return HttpResponseRedirect('http://192.168.33.10:8000/wallet/coindestroysuccess/' + num_of_coins)



def payuser(request):
    amount = request.GET.get('amount')
    print("SUCCESS")

    merchantacc = User.objects.get(username="merchant")
    print(merchantacc)
    print("Balance before: " + str(merchantacc.profile.balance))
    merchantacc.profile.balance = merchantacc.profile.balance + int(amount)
    merchantacc.profile.save()
    print("Balance after: " + str(merchantacc.profile.balance))
    #put money into merchant account here

    return HttpResponse(True)


def testPrepVal(request):
    # PREPARATION STAGE - BL_issuer_preparation
    serialised_entry = request.GET.get('serialised_entry')
    real_C, sessionid = blshim.deserialise(serialised_entry)

    LT_issuer_state = blshim.create_issuer_state()

    msg_to_user_rnd = BLcred.BL_issuer_preparation(LT_issuer_state, real_C)
    print("msg_to_user_rnd: " + str(msg_to_user_rnd))

    # VALIDATION STAGE 1 - BL_issuer_validation
    msg_to_user_aap = BLcred.BL_issuer_validation(LT_issuer_state)

    s = blshim.serialise((msg_to_user_rnd, msg_to_user_aap))

    # can't easily use sessions - browsers
    serialised_C = blshim.serialise(real_C)
    js_cpu = blshim.serialise((LT_issuer_state.cp, LT_issuer_state.u, LT_issuer_state.r1p, LT_issuer_state.r2p))

    j = CoinValidation.objects.get(sessionID=sessionid)

    j.commitment=serialised_C
    j.jsonstring=js_cpu
    j.save()

    ss = DoubleSpendingz1Touser(z1=blshim.serialise(LT_issuer_state.z1), username=j.username)
    ss.save()

    return HttpResponse(s)


def testVal2(request):
    serialised_entry = request.GET.get('serialised_entry')
    real_e, real_c, sessionid = blshim.deserialise(serialised_entry)

    serialised_C = blshim.serialise(real_c)

    db = CoinValidation.objects.get(sessionID=sessionid)

    # need to deduct the money from the user's account
    # and confirm the number of coins requested is the same as that approved earlier 

    LT_issuer_state =  blshim.create_issuer_state()

    LT_issuer_state.cp, LT_issuer_state.u, LT_issuer_state.r1p, LT_issuer_state.r2p = blshim.deserialise(db.jsonstring)

    msg_to_user_crcprp = BLcred.BL_issuer_validation_2(LT_issuer_state, real_e)

    # updating user's balance
    u = User.objects.get(username=db.username)
    u.profile.balance = int(u.profile.balance) - db.num_of_coins
    u.profile.save()

    # finished with "session" so now delete it
    db.delete()

    s = blshim.serialise(msg_to_user_crcprp)

    return HttpResponse(s)


def testvalidation(request):
    valid = True
    error_reason = ""
    list_of_coins_to_put_in_db = []

    serialised_entry = request.GET.get('entry')
    list_of_msgs, desc = blshim.deserialise(serialised_entry)

    #serialiser converts lists to tuples by default
    list_of_msgs = list(list_of_msgs)

    for msg_to_merchant_epmupcoin in list_of_msgs:

        valid_3 = blshim.spending_3(msg_to_merchant_epmupcoin, desc)

        if valid_3:

            # double spending checks here
            (epsilonp, mup, coin) = msg_to_merchant_epmupcoin
            serialise_coin = blshim.serialise(coin)

            try:
                check = DoubleSpendingCoinHistory.objects.get(coin=serialise_coin)
                # now need to extract values saved in it to work out who is spending the coin
                # MATHS
                (epsilonp2, mup2) = blshim.deserialise(check.serialised_entry)

                (m, zet, zet1, zet2, om, omp, ro, ro1p, ro2p) = coin

                z1calc = blshim.doublespendcalc(epsilonp, mup, epsilonp2, mup2, zet1)
         
                z1calc_s = blshim.serialise(z1calc)

                # now we look z1calc in DoubleSpendingz1Touser to find the user..

                guilty_user = DoubleSpendingz1Touser.objects.get(z1=blshim.serialise(z1calc))
                print("@@@@@@@guilty_user: " + guilty_user.username)

                # TODO consquences of naughty db & not let spending happen
                #return HttpResponse(blshim.serialise((False, "DOUBLE SPENDING"))) 
#               valid = not (valid or False)
                valid = False
                error_reason = "DOUBLE SPENDING"
            except DoubleSpendingCoinHistory.DoesNotExist:
                # good - because then there is no double spending
                # add coin to db here

                serialised_entry = blshim.serialise((epsilonp, mup))

                list_of_coins_to_put_in_db.append((serialise_coin, serialised_entry))

        else:
            valid = False
            error_reason = "Coin not a valid coin"


    # need ALL coins to be valid for them to be put the in spent db
    if valid:
        for c in list_of_coins_to_put_in_db:
            serialise_coin, serialised_entry = c
            dc = DoubleSpendingCoinHistory(coin=serialise_coin, serialised_entry=serialised_entry)
            dc.save()

    # also do expiry 
    # update merchant's bank account

    # TODO payuser()

    return HttpResponse(blshim.serialise((valid, error_reason)))