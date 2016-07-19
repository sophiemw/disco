import requests
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from merchant.models import Items

import BLcred, blshim

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
	return render(request, 'merchant/itembuying.html', {'item': item})


def itemsuccess(request, item_id):
	item = get_object_or_404(Items, pk=item_id)

	valid, message = spendingGuts()

	if valid:
		return render(request, 'merchant/itemsuccess.html', {'item': item})
	else:
		return HttpResponse(message)

def spendingGuts():
	desc = blshim.spending_1()
	desc_ser = blshim.serialise(desc)

	print("desc: " + desc_ser)

	r = requests.get('http://192.168.33.10:8000/wallet/testspending/?entry=%s' %(desc_ser))
	c = r.content

	msg_to_merchant_epmupcoin = blshim.deserialise(c)

	# want the validation to happen on the bank side because double spending
	#print("@@@@@" + str(blshim.spending_3(msg_to_merchant_epmupcoin, desc)))

	entry = blshim.serialise((msg_to_merchant_epmupcoin, desc))
	r = requests.get('http://192.168.33.10:8090/bank/testvalidation/?entry=%s' %(entry))
	c = r.content


	return blshim.deserialise(c)

def test_spending_protocol(request):
	

	validated, errormessage = spendingGuts()


#	if validated:
#		r = requests.get('http://192.168.33.10:8090/bank/payuser/?amount=%i' %(item.price))

	print(errormessage)

	return HttpResponse(validated)