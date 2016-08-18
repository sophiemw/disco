from django.conf import settings
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from merchant.models import Category, Items

import BLcred, blshim

import time, requests

fo = open("timings_merchant.csv", "a", 0)

def index(request):
	return HttpResponseRedirect('/merchant/homepage/?category=')

def homepage(request):
	category = request.GET.get('category')

	if category == "":
		all_items = Items.objects.all()
	else:
		all_items = Items.objects.filter(tags__tag=category)
	
	all_categories = Category.objects.all()
	context = {
		'MERCHANT_URL': settings.MERCHANT_URL,
		'all_items': all_items,
		'all_categories': all_categories
	}
	return render(request, 'merchant/homepage.html', context)


def itemdetail(request, item_id):
	item = get_object_or_404(Items, pk=item_id)
	return render(request, 'merchant/itemdetail.html', {'item': item})


def itembuying(request, item_id):
	item = get_object_or_404(Items, pk=item_id)
	context = {
		'item': item,
		'WALLET_URL': settings.WALLET_URL
		}
	return render(request, 'merchant/itembuying.html', context)


def itemsuccess(request):
	item_id, sessionid = blshim.deserialise(request.GET.get('entry'))

	item = get_object_or_404(Items, pk=item_id)

	im = "merchantbankaccount"
	start = time.time()
	desc = blshim.spending_1(im)
	fo.write("blshim.spending_1, " + str(time.time() - start) + "\n")
	
	serialised_entry = blshim.serialise((desc, sessionid, im))

	start = time.time()
	r = requests.get(settings.WALLET_URL + '/ws_coin_list/?entry=%s' %(serialised_entry))
	fo.write("wallet/ws_coin_list, " + str(time.time() - start) + "\n")
	c = r.content

	valid, error_reason, list_of_msgs = blshim.deserialise(c)

	if valid:
		# want the validation to happen on the bank side because double spending

		# sending all coins to the bank at once
		entry = blshim.serialise((list_of_msgs, desc, im, item.price))

		start = time.time()
		r = requests.get(settings.BANK_URL + '/ws_spend_reveal/?entry=%s' %(entry))
		fo.write("bank/ws_spend_reveal, " + str(time.time() - start) + "\n")
		c = r.content
 
		valid, error_reason = blshim.deserialise(c)

	if valid:
		return render(request, 'merchant/itemsuccess.html', {'item': item})
	else:
		return HttpResponse(error_reason)


def itemsuccess2(request, item_id):
	item = get_object_or_404(Items, pk=item_id)
	return render(request, 'merchant/itemsuccess2.html', {'item': item})
