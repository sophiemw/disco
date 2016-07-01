from django.conf.urls import url

from . import views

app_name = 'wallet'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'signup/$', views.signup, name='signup'),
    url(r'login/$', views.login, name='login'),
    url(r'homepage/$', views.homepage, name='homepage'),
]