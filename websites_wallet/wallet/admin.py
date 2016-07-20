from django.contrib import admin

from wallet.models import PaymentSession, Coins

admin.site.register(Coins)
admin.site.register(PaymentSession)