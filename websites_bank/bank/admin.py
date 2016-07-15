from django.contrib import admin

# Register your models here.
#from .models import User
from models import CoinValidation, UserProfile

#admin.site.register(Users)
admin.site.register(UserProfile)
admin.site.register(CoinValidation)
