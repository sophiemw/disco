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

]