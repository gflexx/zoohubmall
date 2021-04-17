from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q

from .utils import get_client_ip
from .models import SearchItem
from products.models import Product, Store
from bag.models import Bag

def search_view(request):
	template_name = 'search.html'
	search_input = request.GET.get('q')
	if search_input is not None:
		if len(str(search_input)) > 0:
			search_item = SearchItem.objects.create(
				search = search_input,
				ip = get_client_ip(request),
				time = timezone.now()
			)
		look_up = (Q(name__icontains=search_input) | Q(description__icontains=search_input) | Q(price__icontains=search_input))
		products = Product.objects.all().filter(look_up).distinct().order_by('-price')
		num_results = products.count()
		prds = Product.objects.all().is_active()
		total = sum([prodct.quantity for prodct in prds])
		bag, is_new = Bag.objects.bag_id(request)
		context = {
			'title': 'Search for ' + search_input,
			'num_results': num_results,
			'products': products,
			'prds': prds,
			'total': total,
			'bag': bag,
			'search_input': search_input,
		}
		return render(request, template_name, context)
	
def store_search(request):
	template_name = 'store_search.html'
	search_input = request.GET.get('q')
	if search_input is not None:
		look_up = (Q(name__icontains=search_input) | Q(description__icontains=search_input))
		stores = Store.objects.all().filter(look_up).distinct().order_by('-views')
		num_results = stores.count()
		strs = Store.objects.filter(is_active=True).count()
		context = {
			'title': 'Search for ' + search_input,
			'stores': stores,
			'num_results': num_results,
			'search_input': search_input,
			'strs': strs,
		}
		return render(request, template_name, context)

