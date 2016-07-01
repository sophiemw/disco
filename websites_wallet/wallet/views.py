from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return render(request, 'wallet/index.html')

def signup(request):
	return HttpResponse("This is the signup page")

def login(request):
	return HttpResponse("This is the log in page")

def homepage(request):
	return HttpResponse("This is the home page - when logged in (eventually)")