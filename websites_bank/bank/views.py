from django import forms
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext, loader

from bank.forms import RegisterForm
from bank.models import UsersWhoHaveDoubleSpent, DoubleSpendingCoinHistory, DoubleSpendingz1Touser, CoinValidation, UserProfile

import blshim, BLcred

import time, datetime

fo = open("timings_bank.csv", "a", 0)

def user_login(request):
    # http://stackoverflow.com/questions/16750464/django-redirect-after-login-not-working-next-not-posting
    # Obtain the context for the user's request.
    context = RequestContext(request)
    next = ""
    if request.GET:  
        next = request.GET['next']

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
        return render(request, 'bank/login.html', {'next': next})


# http://www.tangowithdjango.com/book/chapters/login.html
# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/bank/')


def register(request):
	# https://docs.djangoproject.com/en/1.9/topics/forms/
    # http://www.tangowithdjango.com/book/chapters/login.html#creating-a-user-registration-view-and-template
	# http://stackoverflow.com/questions/8917185/in-django-when-i-call-user-objects-create-userusername-email-password-why

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
			# process the data in form.cleaned_data as required
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
            return HttpResponseRedirect('/bank/')
            
    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegisterForm()

    return render(request, 'bank/register.html', {'form': form})


@login_required
def homepage(request):
    return render(request, 'bank/homepage.html')

#########################################################################################
# User - coin creation
@login_required
def coincreation(request, num_of_coins):
    return render(request, 'bank/coincreation.html', {'num_of_coins': num_of_coins})


@login_required
def confirmcoincreation(request, num_of_coins):
    # User has confirmed wanting to make the coins, updates bank balance
    # and starts the crypto process
    new_balance = int(request.user.profile.balance) - int(num_of_coins)

    if (new_balance) < 0:
        return HttpResponse("Bank: Cannot create coins - insufficient funds")
    else:
        # We need to track a number of variables across a number of webservice calls
        # so capture these in a session db
        sessionid = request.session._session_key

        # Remove any old entries that might have been created by defects
        CoinValidation.objects.filter(sessionID=sessionid).delete()
    
        CoinValidation(sessionID=sessionid, user=request.user, num_of_coins=num_of_coins, commitment="", jsonstring="").save()
        
        entry = blshim.serialise((int(num_of_coins), sessionid))
        return HttpResponseRedirect(settings.WALLET_URL + '/coinsuccess/?entry=%s' %(entry))


#########################################################################################
# Coin creation - webservice call
def ws_preparation_validation_1(request):
    # PREPARATION STAGE - BL_issuer_preparation
    serialised_entry = request.GET.get('serialised_entry')
    pi_proof_values, real_C, sessionid, value_of_coin, expirydate = blshim.deserialise(serialised_entry)

    # Standard non-interactive proof of knowledge - pi proof
    # validation that the coin value and expiry date have been set correctly by the wallet
    start = time.time()
    pi_proof_bank = blshim.pi_proof_bank(pi_proof_values)
    fo.write("blshim.pi_proof_bank, " + str(time.time() - start) + "\n")

    if pi_proof_bank:
        start = time.time()
        LT_issuer_state = blshim.create_issuer_state()
        fo.write("blshim.create_issuer_state, " + str(time.time() - start) + "\n")

        start = time.time()
        msg_to_user_rnd = BLcred.BL_issuer_preparation(LT_issuer_state, real_C)
        fo.write("BLcred.BL_issuer_preparation, " + str(time.time() - start) + "\n")
        
        # VALIDATION STAGE 1 - BL_issuer_validation
        start = time.time()
        msg_to_user_aap = BLcred.BL_issuer_validation(LT_issuer_state)
        fo.write("BLcred.BL_issuer_validation, " + str(time.time() - start) + "\n")
        
        results = msg_to_user_rnd, msg_to_user_aap

        # can't easily use sessions - browsers
        serialised_C = blshim.serialise(real_C)
        js_cpu = blshim.serialise((LT_issuer_state.cp, LT_issuer_state.u, LT_issuer_state.r1p, LT_issuer_state.r2p))

        session_details = CoinValidation.objects.get(sessionID=sessionid)
        session_details.commitment=serialised_C
        session_details.jsonstring=js_cpu
        session_details.save()

        DoubleSpendingz1Touser(z1=blshim.serialise(LT_issuer_state.z1), user=session_details.user, expirydate=expirydate, value_of_coin=value_of_coin).save()

        return HttpResponse(blshim.serialise((True, results)))
    else:
        return HttpResponse(blshim.serialise((False, "problems with pi proof")))


def ws_validation_2(request):
    serialised_entry = request.GET.get('serialised_entry')
    real_e, real_c, sessionid = blshim.deserialise(serialised_entry)

    serialised_C = blshim.serialise(real_c)

    db = CoinValidation.objects.get(sessionID=sessionid)

    # need to deduct the money from the user's account
    # and confirm the number of coins requested is the same as that approved earlier 
    start = time.time()
    LT_issuer_state =  blshim.create_issuer_state()
    fo.write("blshim.create_issuer_state, " + str(time.time() - start) + "\n")

    LT_issuer_state.cp, LT_issuer_state.u, LT_issuer_state.r1p, LT_issuer_state.r2p = blshim.deserialise(db.jsonstring)

    start = time.time()
    msg_to_user_crcprp = BLcred.BL_issuer_validation_2(LT_issuer_state, real_e)
    fo.write("BLcred.BL_issuer_validation_2, " + str(time.time() - start) + "\n")

    # updating user's balance
    u = db.user
    u.profile.balance = int(u.profile.balance) - db.num_of_coins
    u.profile.save()

    # finished with "session" so now delete it
    db.delete()

    return HttpResponse(blshim.serialise(msg_to_user_crcprp))


#########################################################################################
# Coin spending
def ws_spend_reveal(request):
    valid = True
    error_reason = ""
    list_of_coins_to_put_in_db = []

    serialised_entry = request.GET.get('entry')
    list_of_msgs, desc, im, amount = blshim.deserialise(serialised_entry)

    #serialiser converts lists to tuples by default
    list_of_msgs = list(list_of_msgs)

    for coin_with_reveals in list_of_msgs:
        msg_to_merchant_epmupcoin, amount_rev_values, expiry_rev_values, value_of_coin, expirydate = coin_with_reveals

        start = time.time()
        valid_3 = blshim.spending_3(msg_to_merchant_epmupcoin, desc)
        fo.write("blshim.spending_3, " + str(time.time() - start) + "\n")
        
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

                start = time.time()
                z1calc = blshim.doublespendcalc(epsilonp, mup, epsilonp2, mup2, zet1)
                fo.write("blshim.doublespendcalc, " + str(time.time() - start) + "\n")
                         
                z1calc_s = blshim.serialise(z1calc)

                # now we look z1calc in DoubleSpendingz1Touser to find the user..
                guilty_user = DoubleSpendingz1Touser.objects.get(z1=blshim.serialise(z1calc))

                # Add guilty user to a list of all users who have double spent
                n = UsersWhoHaveDoubleSpent(user=guilty_user.user, coin=serialise_coin, serialised_entry=check.serialised_entry)
                n.save()

#               valid = not (valid or False)
                valid = False
                error_reason = "DOUBLE SPENDING"
            except DoubleSpendingCoinHistory.DoesNotExist:
                # good - because then there is no double spending
                # add coin to db here
                serialised_entry = blshim.serialise((epsilonp, mup))

                list_of_coins_to_put_in_db.append((serialise_coin, serialised_entry))

                # check coin's attributes - value, expiry date
                start = time.time()
                coin_value_valid, Lj_value = blshim.rev_attribute_2(amount_rev_values)
                fo.write("blshim.rev_attribute_2, " + str(time.time() - start) + "\n")

                start = time.time()
                coin_expiry_valid, Lj_expirydate = blshim.rev_attribute_2(expiry_rev_values)
                fo.write("blshim.rev_attribute_2, " + str(time.time() - start) + "\n")

                if coin_value_valid:
                    valid = Lj_value == value_of_coin
                    if valid and coin_expiry_valid:
                        # http://www.saltycrane.com/blog/2008/06/how-to-get-current-date-and-time-in/
                        now = datetime.datetime.now() 
                        valid = (Lj_expirydate == expirydate) and (expirydate > now.year)
                        if not valid: error_reason = "Coin expired"
                    else:
                        valid = False
                        error_reason = "Coin not valid"
                else:
                    valid = False
                    error_reason = "Coins values are different"

        else:
            valid = False
            error_reason = "Coin not a valid coin"

    # need ALL coins to be valid for them to be put the in spent db
    if valid:
        for c in list_of_coins_to_put_in_db:
            serialise_coin, serialised_entry = c
            dc = DoubleSpendingCoinHistory(coin=serialise_coin, serialised_entry=serialised_entry)
            dc.save()

    # update merchant's bank account
    merchantacc = User.objects.get(username=im)
    merchantacc.profile.balance = merchantacc.profile.balance + int(amount)
    merchantacc.profile.save()

    return HttpResponse(blshim.serialise((valid, error_reason)))

#########################################################################################
# Coin destroying
@login_required
def coindestroy(request, num_of_coins, coinpk):
    context = {
        'num_of_coins': num_of_coins,
        'coinpk': coinpk
    }
    return render(request, 'bank/coindestroy.html', context)


@login_required
def coindestroysuccess(request, num_of_coins, coinpk):
    request.user.profile.balance = request.user.profile.balance + int(num_of_coins)
    request.user.profile.save()
    return HttpResponseRedirect(settings.WALLET_URL + '/coindestroysuccess/' + num_of_coins + "/" + coinpk)