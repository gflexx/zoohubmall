from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib import messages

from .forms import *
from .models import *
from bag.models import Bag
from analytics.models import ObjectViewed, get_client_ip
from analytics.signals import object_viewed_signal

def categories(request):
	template_name = 'categories.html'
	context = {
		'title': 'Categories'
	}
	return render(request, template_name, context)

def category_view(request, slug):
	template_name = 'category_view.html'
	category = get_object_or_404(Category, slug=slug)
	recommended = Product.objects.recommended()[:4]	
	products = Product.objects.is_active().filter(category=category)
	category.views += 1
	category.save()
	bag, is_new = Bag.objects.bag_id(request)
	meta_keywords = category.name
	site_description = category.description
	paginator = Paginator(products, 12)
	page = request.GET.get('page')
	try:
		products = paginator.get_page(page)
	except PageNotInteger:
		products = paginator(1)
	except EmptyPage:
		products = paginator.page(paginator.num_pages)
	object_viewed_signal.send(category.__class__, instance=category, request=request)
	context = {
		'title': category.name,
		'category': category,
		'products': products,
		'recommended': recommended,
		'meta_keywords': meta_keywords,
		'site_description': site_description,
		'bag': bag,
	}
	return render(request, template_name, context)
	
def product_view(request, slug):
	template_name = 'product_page.html'
	product = get_object_or_404(Product, slug=slug)
	bestselling = Product.objects.bestseller()[:3]
	featured = Product.objects.featured()[:3]
	recommended = Product.objects.recommended()[:3]
	comments = Comment.objects.filter(product=product).order_by('-created_at')
	product.views += 1
	product.save()
	form = CommentCreationForm()
	meta_keywords = product.name
	site_description = product.description
	object_viewed_signal.send(product.__class__, instance=product, request=request)
	ip_address = get_client_ip(request)
	product_type = ContentType.objects.get(app_label='products', model='product')	
	prev_views = ObjectViewed.objects.filter(content_type=product_type).order_by('object_id', '-timestamp').distinct('object_id').exclude(object_id=product.id)
	if request.user.is_authenticated:
		user_mail = request.user.email
		previous_views = prev_views.filter(user_email=user_mail)[:6]
	else:
		previous_views = prev_views.filter(ip_address=ip_address)[:6]
	object_viewed_signal.send(product.__class__, instance=product, request=request)
	context = {
		'title': product.name,
		'product': product,
		'bestselling': bestselling,
		'featured': featured,
		'recommended': recommended,
		'previous_views': previous_views,
		'comments': comments,
		'form': form,
		'meta_keywords': meta_keywords,
		'site_description': site_description,
	}
	return render(request, template_name, context)
	
@csrf_exempt
def product_comment(request):
	if request.method == 'POST':	
		form  = CommentCreationForm(request.POST)
		if form.is_valid():
			text = request.POST.get('text')
			product_slug = request.POST.get('product_slug')
			product = get_object_or_404(Product, slug=product_slug)
			comment = Comment.objects.create(
				posted_by = request.user,
				product = product,
				text = text,
			)
			msg = 'Comment Posted'
			if request.is_ajax():
				comments = Comment.objects.filter(product=product).order_by('-created_at')
				num_comments = comments.count()
				context = {
					'comments': comments,
				}
				html = render_to_string('includes/comments.html', context, request=request)
				data = {
					'comments': html,
					'messageLoad': msg,
					'numComments': num_comments,
				}
				return JsonResponse(data)
			messages.success(request, msg)
			return redirect(product.get_absolute_url())

def store_view(request, slug):
	template_name = 'store_view.html'
	store = get_object_or_404(Store, slug=slug)
	if request.method == 'POST':
		form  = ReviewCreationForm(request.POST)
		if form.is_valid():
			text = request.POST.get('text')
			next = request.POST.get('next')
			review = Review.objects.create(
				posted_by = request.user,
				store = store,
				text = text,
			)
			msg = 'Review Posted'
			if request.is_ajax():
				reviews = Review.objects.filter(store=store).order_by('-created_at')
				num_reviews = reviews.count()
				context = {
					'reviews': reviews,
				}
				html = render_to_string('includes/reviews.html', context, request=request)
				data = {
					'reviews': html,
					'messageLoad': msg,
					'numReviews': num_reviews,
				}
				return JsonResponse(data)
			messages.success(request, msg)
			return redirect(next)
	products = Product.objects.filter(store=store)
	bag, is_new = Bag.objects.bag_id(request)
	uri = request.build_absolute_uri()
	reviews = Review.objects.filter(store=store).order_by('-id')
	total = sum([product.quantity for product in products])
	form = ReviewCreationForm()
	store.views += 1
	store.save()
	meta_keywords = store.name
	site_description = store.description
	paginator = Paginator(products, 12)
	page = request.GET.get('page')
	try:
		products = paginator.get_page(page)
	except PageNotInteger:
		products = paginator(1)
	except EmptyPage:
		products = paginator.page(paginator.num_pages)
	object_viewed_signal.send(store.__class__, instance=store, request=request)
	context = {
		'title': store.name,
		'store': store,
		'products': products,
		'reviews': reviews,
		'bag': bag,
		'uri': uri,
        'total': total,
		'form': form,
		'meta_keywords': meta_keywords,
		'site_description': site_description,	
	}
	return render(request, template_name, context)

def stores(request):
	template_name = 'stores.html'
	open_stores = Store.objects.filter(is_active=True)
	trending = Store.objects.filter(is_active=True).order_by('-views')[:6]
	paginator = Paginator(open_stores, 12)
	page = request.GET.get('page')
	try:
		open_stores = paginator.get_page(page)
	except PageNotInteger:
		open_stores = paginator(1)
	except EmptyPage:
		open_stores = paginator.page(paginator.num_pages)
	context = {
		'title': 'Open Stores',
		'stores': open_stores,
        'trending': trending,
	}
	return render(request, template_name, context)

