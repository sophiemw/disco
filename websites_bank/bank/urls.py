from django.conf.urls import url

from . import views

app_name = 'bank'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^(?P<user_id>[0-9]+)/$', views.homepage, name='homepage'),
    url(r'homepage/$', views.homepage, name='homepage'),
    url(r'signup/$', views.signup, name='signup'),
    url(r'userlist/$', views.userlist, name='userlist'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^coincreation/(?P<num_of_coins>[0-9]+)/$', views.coincreation, name='coincreation'),
    url(r'^confirmcoincreation/(?P<num_of_coins>[0-9]+)/$', views.confirmcoincreation, name='confirmcoincreation'),
]