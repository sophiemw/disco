from django.conf.urls import url

from . import views

app_name = 'merchant'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<item_id>[0-9]+)/$', views.itemdetail, name='itemdetail'),
    url(r'^(?P<item_id>[0-9]+)/buy/$', views.itembuying, name='itembuying'),
    url(r'^(?P<item_id>[0-9]+)/success/$', views.itemsuccess, name='itemsuccess'),
	url(r'test_spending_protocol/$', views.test_spending_protocol, name='test_spending_protocol'),
]