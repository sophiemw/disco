from django.contrib import auth
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader

from .forms import SignupForm
from .models import Users

def index(request):
    return HttpResponse("Hello, world. You're at the bank index. aka sign in page")

def signup(request):
	# if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SignupForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('bank:homepage', args=(1,)))
            
    # if a GET (or any other method) we'll create a blank form
    else:
        form = SignupForm()

    return render(request, 'bank/signup.html', {'form': form})

def homepage(request, user_id):
	return HttpResponse("User page for user id: %s" % user_id)

def userlist(request):
	user_list = Users.objects.all()
	context = {
		'user_list': user_list,
	}
	return render(request, 'bank/userlist.html', context)