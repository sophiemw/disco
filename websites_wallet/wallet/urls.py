from django.conf.urls import url

from . import views

app_name = 'wallet'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'signup/$', views.signup, name='signup'),
    url(r'login/$', views.userlogin, name='login'),
    url(r'logout/$', views.userlogout, name='logout'),
    url(r'homepage/$', views.homepage, name='homepage'),
    url(r'^(?P<user_getting_money>[A-Za-z0-9\-\_]+)/(?P<payment_amount>[0-9]+)/(?P<item_id>[0-9]+)/$', views.payment, name='payment'),
]
