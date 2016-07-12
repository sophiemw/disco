import requests
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from merchant.models import Items

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

	r = requests.get('http://192.168.33.10:8090/bank/payuser/?amount=%i' %(item.price))
	
	return render(request, 'merchant/itemsuccess.html', {'item': item})