from django.shortcuts import render

from products.models import Product, Category, Store
from bag.models import Bag

def home(request):
	template_name = 'home.html'
	recent = Product.objects.is_active().order_by('-uploaded_at')[:12]
	trending = Product.objects.is_active().order_by('-views')[:10]
	categories = Category.objects.filter(is_active=True).order_by('-views')[:8]
	stores = Store.objects.filter(is_featured=True)[:6]
	bag, is_new = Bag.objects.bag_id(request)
	context = {
		'title': 'Home',
		'recent': recent,
        'trending': trending,
        'popular_categories': categories,
        'stores': stores,
        'bag': bag,
	}
	return render(request, template_name, context)

def about(request):
	template_name = 'about.html'
	context = {
		'title': 'About',
	}
	return render(request, template_name, context)
	
def help(request):
	template_name = 'help.html'
	context = {
		'title': 'Help',
	}
	return render(request, template_name, context)
	
def contact(request):
	template_name = 'contact.html'
	context = {
		'title': 'Contact Us',
	}
	return render(request, template_name, context)
	
def terms(request):
	template_name = 'terms.html'
	context = {
		'title': 'Terms and Conditions',
	}
	return render(request, template_name, context)
	
def privacy(request):
	template_name = 'privacy.html'
	context = {
		'title': 'Privacy Policy',
	}
	return render(request, template_name, context)	
