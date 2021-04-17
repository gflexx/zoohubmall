from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response

from .forms import *
from .models import Customer, Guest
from bag.models import Bag
from bag.views import get_total_items
from orders.models import Order, ProductPurchase
from products.models import *
from products.forms import *

def is_seller(user):
	if user.customer.is_seller:
		return True
	else:
		raise PermissionDenied

@login_required
def profile(request):
	template_name = 'profile.html'
	bag = Bag.objects.check_owner(request)
	if bag is not None:
		request.session['bag_id'] = bag.bag_identity
		total_quantity = get_total_items(request)
		request.session['num_products'] = total_quantity
	uri = request.build_absolute_uri()
	customer_selection = CustomerSelectionForm()
	user_update = UserUpdateForm(instance=request.user)
	context = {
		'title': 'Profile',
		'uri': uri,
		'customer_selection': customer_selection,
		'user_update': user_update,
	}
	return render(request, template_name, context)
	
def update_user(request):
	if request.method == 'POST':
		user_update = UserUpdateForm(request.POST, request.FILES, instance=request.user)
		if user_update.is_valid():
			if user_update.has_changed():
				user_update.save()
				msg = 'User details updated successfully'
				messages.success(request, msg)
				return redirect('users:profile')
			else:
				return redirect('users:profile')
		else:
			user_update.add_error(None, "Something's wrong, check your values")	
	
def customer_profile_creation(request):
	if request.method == 'POST':
		usr = Customer.objects.get(user=request.user)
		form = CustomerSelectionForm(request.POST, instance=usr)
		next = request.POST.get('next')
		redirect_path = next
		if form.is_valid():
			customer = form.save(commit=False)
			customer.profile_creation_complete = True
			customer.save()
			msg = 'Account created successfully'
			messages.success(request, msg)
			if is_safe_url(redirect_path, request.get_host()):
				return redirect(redirect_path)
		else:
			form.add_error(None, "Something's wrong, check your values")
		return redirect('users:profile')
		
def custom_login(request):
	form = UserLoginForm(request.POST)
	next = request.POST.get('next')
	if form.is_valid():
		email = form.cleaned_data['email']
		password = form.cleaned_data['password']
		user = authenticate(email=email, password=password)
		if user is not None:
			login(request, user)
			if is_safe_url(next, request.get_host()):
				return redirect(next)
		else:
			if request.is_ajax():
				form = UserLoginForm()
				context = {
					'form': form,
					'next': next,
				}
				html = render_to_string(context, 'includes/custom_login.html', request=request)
				data = {
					'html': html,
				}
				return JsonResponse(data)
			msg = 'Incorrect Email or Password'
			messages.success(request, msg)
			return redirect('checkout:checkout_view')
	else:
		form.add_error(None, 'Something\'s wrong, check your values.')

def guest_register(request):
	form = GuestEmailForm(request.POST or None)
	next = request.POST.get('next')
	if form.is_valid():
		email = form.cleaned_data['email']
		new_guest = Guest.objects.create(email=email)
		request.session['guest_id'] = new_guest.id
		if is_safe_url(next, request.get_host()):
			return redirect(next)
		
@login_required
def dashboard(request):
	template_name = 'dashboard.html'
	store = Store.objects.filter(owner=request.user)
	create_store = StoreCreationForm()
	context = {
		'title': 'Dashboard',
		'store_data': store,
		'create_store': create_store,
	}
	return render(request, template_name, context)

def create_store(request):
	if request.method == 'POST':
		form = StoreCreationForm(request.POST)
		if form.is_valid():
			store_name = form.cleaned_data['name']
			create_store = form.save(commit=False)
			create_store.owner = request.user
			create_store.save()
			msg = store_name + ' created successfully'
			messages.success(request, msg)
			return redirect('users:dashboard')
		else:
			form.add_error(None, "Something's wrong, check your values")

@login_required
def orders_view(request):
	template_name = 'orders_view.html'
	customer_profile = Customer.objects.get(user=request.user)
	previous_orders = Order.objects.filter(customer=customer_profile, status='paid')
	context = {
		'title': 'Your Orders',
		'previous_orders': previous_orders,
	}
	return render(request, template_name, context)
	
@login_required
def purchase_history(request):
	customer_profile = Customer.objects.get(user=request.user)
	previous_purchase = ProductPurchase.objects.filter(customer=customer_profile)
	template_name = 'purchase_history.html'
	context = {
		'title': 'Product Purchase History',
		'previous_purchase': previous_purchase,
	}
	return render(request, template_name, context)

# store views
@login_required
@user_passes_test(is_seller)	
def add_product(request):
	template_name = 'add_product.html'
	store = Store.objects.get(owner=request.user)
	if request.method == 'POST':
		form = ProductCreationForm(request.POST, request.FILES)	
		if form.is_valid():
			product_name = form.cleaned_data['name']
			product_add = form.save(commit=False)
			product_add.store = store
			product_add.save()
			form.save_m2m()
			msg = product_name + ' added successfully'
			messages.success(request, msg)
			return redirect('users:dashboard')
		else:
			form.add_error(None, "Something's wrong, please check your values")
	form = ProductCreationForm()
	context = {
		'title': 'Add product',
		'form': form,
		'store': store
	}
	return render(request, template_name, context)

@user_passes_test(is_seller)	
@login_required
def all_products(request):
	template_name = 'all_products.html'
	store = Store.objects.get(owner=request.user)
	products = Product.objects.filter(store=store)
	context = {
		'title': 'Products for ' + store.name,
		'store': store,
		'products': products,
	}
	return render(request, template_name, context)

@login_required	
@user_passes_test(is_seller)	
def stock(request):
	template_name = 'stock.html'
	store = Store.objects.get(owner=request.user)
	products = Product.objects.filter(store=store)
	num_products = sum([product.quantity for product in products])
	context = {
		'title': 'Product stock for ' + store.name,
		'store': store,
		'products': products,
		'num_products': num_products,
	}
	return render(request, template_name, context)
	
@login_required
@user_passes_test(is_seller)
def update_store(request):
	template_name = 'store_update.html'
	store = Store.objects.get(owner=request.user)
	if request.method == 'POST':
		form = StoreUpdateForm(request.POST, instance=store)
		if form.is_valid():
			if form.has_changed():
				store_update = form.save(commit=False)
				store_update.updated_at = timezone.now()
				store_update.save()
				msg = 'Store details updated succesfully'
				messages.success(request, msg)
				return redirect('users:dashboard')
			else:
				return redirect('users:update_store')
		else:
			form.add_error(None, "Somethimg's wrong, check your values")
	form = StoreUpdateForm(instance=store)
	context = {
		'title': 'Edit store details',
		'store': store,
		'form': form,
	}
	return render(request, template_name, context)

@login_required
@user_passes_test(is_seller)
def delete_store(request, slug):
	store = Store.objects.get(slug=slug)
	if store.owner.email == request.user.email:
		store.delete()
		msg = store.name + ' deleted succesfully'
		messages.success(request, msg)
		return redirect('users:dashboard')
	else:
		raise PermissionDenied

@login_required
@user_passes_test(is_seller)
def update_product(request, slug):
	template_name = 'update_product.html'
	store = Store.objects.get(owner=request.user)
	product = Product.objects.get(slug=slug)
	if request.method == 'POST':
		form = ProductUpdateForm(request.POST, request.FILES, instance=product)
		if form.is_valid():
			if form.has_changed():
				change_product = form.save(commit=False)
				change_product.updated_at = timezone.now()
				change_product.save()
				form.save_m2m()
				msg = product.name + ' updated successfully'
				messages.success(request, msg)
				return redirect('users:all_products')
			else:
				return redirect('users:update_product', slug=product.slug)
		else:
			form.add_error(None, "Something's wrong, check your values")
	form = ProductUpdateForm(instance=product)
	context = {
		'title': 'Product Update',
		'store': store,
		'form': form,
		'product': product,
	}
	return render(request, template_name, context)

@login_required
@user_passes_test(is_seller)
def delete_product(request, slug):
	product = Product.objects.get(slug=slug)
	if product.store.owner.email == request.user.email:
		product.delete()
		msg = product.name + ' deleted succesfully'
		messages.success(request, msg)
		return redirect('users:all_products')
	else:
		raise PermissionDenied

@login_required
@user_passes_test(is_seller)
def metrics(request):
	template_name = 'metrics.html'
	store = Store.objects.get(owner=request.user)
	products = Product.objects.filter(store=store)	
	purchased_products = ProductPurchase.objects.filter(store=store)
	month_sales = purchased_products.filter(created_at__month=datetime.now().month).order_by('-created_at')
	num_purchases = sum([purchase.quantity for purchase in purchased_products])
	total_products = sum([product.quantity for product in products])
	product_views = sum([product.views for product in products])
	total_sales = sum([product.price for product in purchased_products])
	total_month_sales = sum([product.price for product in month_sales])
	context = {
		'title': 'Metrics for ' + store.name,
		'store': store,
		'products': products,
		'purchased_products': purchased_products,
		'total_products': total_products,
		'total_sales': total_sales,
		'total_month_sales': total_month_sales,
		'month_sales': month_sales,
		'num_purchases': num_purchases,
		'total_products': total_products,
		'product_views': product_views,
	}
	return render(request, template_name, context)
	
class ChartApi(APIView):
	authentication_classes = []
	permission_classes = []
	def get(self, request, format=None):
		product_names = ["x", "y", "z", "k"]
		product_views = [2, 4, 5, 6]
		data = {
			"productNames": product_names,
			"productViews": product_views,
		}
		return Response(data)
		
chart_api = ChartApi.as_view()

@login_required
@user_passes_test(is_seller)	
def store_orders(request):
	template_name = 'store_orders.html'
	store = Store.objects.get(owner=request.user)
	purchased_products = ProductPurchase.objects.filter(store=store)
	context = {
		'title': 'Store Orders',
		'store': store,
		'purchased_products': purchased_products,
	}
	return render(request, template_name, context)
	
	