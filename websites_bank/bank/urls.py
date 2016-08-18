from django.conf.urls import url

from . import views

app_name = 'bank'
urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^coincreation/(?P<num_of_coins>[0-9]+)/$', views.coincreation, name='coincreation'),
    url(r'^confirmcoincreation/(?P<num_of_coins>[0-9]+)/$', views.confirmcoincreation, name='confirmcoincreation'),
    url(r'^coindestroy/(?P<num_of_coins>[0-9]+)/(?P<coinpk>[0-9]+)/$', views.coindestroy, name='coindestroy'),
    url(r'^coindestroysuccess/(?P<num_of_coins>[0-9]+)/(?P<coinpk>[0-9]+)/$', views.coindestroysuccess, name='coindestroysuccess'),
    url(r'ws_preparation_validation_1/$', views.ws_preparation_validation_1, name='ws_preparation_validation_1'),
    url(r'ws_validation_2/$', views.ws_validation_2, name='ws_validation_2'),
    url(r'ws_spend_reveal/$', views.ws_spend_reveal, name='ws_spend_reveal'),
]