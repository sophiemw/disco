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
	#return HttpResponse("Item page for item %s." % item_id)
	#try:
	#	item = Items.objects.get(pk=item_id)
	#except Items.DoesNotExist:
	#	raise Http404("Item does not exist")
	#return render(request, 'merchant/itemdetail.html', {'item': item})


	item = get_object_or_404(Items, pk=item_id)
	return render(request, 'merchant/itemdetail.html', {'item': item})


def itembuying(request, item_id):
	return HttpResponse("Buying item page for item %s." % item_id)


def itemsuccess(request, item_id):
	return HttpResponse("Item bought successfully page for item %s." % item_id)