from django.conf.urls import url

from . import views

app_name = 'wallet'
urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'register/$', views.register, name='register'),
    url(r'login/$', views.user_login, name='login'),
    url(r'logout/$', views.user_logout, name='logout'),
    url(r'^(?P<payment_amount>[0-9]+)/(?P<item_id>[0-9]+)/$', views.payment, name='payment'),
    url(r'coinsuccess/$', views.coinsuccess, name='coinsuccess'),
    url(r'coinsuccess2/$', views.coinsuccess2, name='coinsuccess2'),
    url(r'convertingcoinsbacktomoney/(?P<coinnum>[0-9]+)/(?P<coinpk>[0-9]+)/$', views.convertingcoinsbacktomoney, name='convertingcoinsbacktomoney'),
    url(r'^coindestroysuccess/(?P<num_of_coins>[0-9]+)/(?P<coinpk>[0-9]+)/$', views.coindestroysuccess, name='coindestroysuccess'),
    url(r'^coindestroysuccess2/(?P<num_of_coins>[0-9]+)/$', views.coindestroysuccess2, name='coindestroysuccess2'),
	url(r'create_coins/$', views.create_coins, name='create_coins'),
    url(r'ws_coin_list/$', views.ws_coin_list, name='ws_coin_list'),
]
