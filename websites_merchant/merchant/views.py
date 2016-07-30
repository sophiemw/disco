from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from merchant.models import Items

import BLcred, blshim

import requests

def index(request):
    #return HttpResponse("Hello, world. You're at the index.")
    all_items = Items.objects.all()
    context = {
    	'all_items': all_items
    }
    return render(request, 'merchant/index.html', context)


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
	desc = blshim.spending_1(im)
	serialised_entry = blshim.serialise((desc, sessionid, im))

	r = requests.get(settings.WALLET_URL + '/testspending/?entry=%s' %(serialised_entry))
	c = r.content

	valid, error_reason, list_of_msgs = blshim.deserialise(c)

	if valid:
		# want the validation to happen on the bank side because double spending

		# sending all coins to the bank at once
		entry = blshim.serialise((list_of_msgs, desc, im, item.price))
		r = requests.get(settings.BANK_URL + '/testvalidation/?entry=%s' %(entry))
		c = r.content
 
		valid, error_reason = blshim.deserialise(c)

	if valid:
		return render(request, 'merchant/itemsuccess.html', {'item': item})
	else:
		return HttpResponse(error_reason)


def itemsuccess2(request, item_id):
	item = get_object_or_404(Items, pk=item_id)
	return render(request, 'merchant/itemsuccess2.html', {'item': item})
