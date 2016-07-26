from django.contrib import admin

from models import UsersWhoHaveDoubleSpent, DoubleSpendingCoinHistory, DoubleSpendingz1Touser, CoinValidation, UserProfile

admin.site.register(UserProfile)
admin.site.register(CoinValidation)
admin.site.register(DoubleSpendingz1Touser)
admin.site.register(DoubleSpendingCoinHistory)
admin.site.register(UsersWhoHaveDoubleSpent)