from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.contrib import messages
from decimal import Decimal as _Decimal

from .forms import *
from users.forms import UserLoginForm
from addresses.models import Address
from bag.models import Bag, BagItem
from bag.views import get_bag_items, get_total_items
from orders.models import Order, ProductPurchase
from products.models import Product
from users.forms import GuestEmailForm
from users.models import Customer, Guest

def checkout(request):
	template_name = 'checkout.html'
	bag, bag_created = Bag.objects.bag_id(request)
	bag_items = get_bag_items(request)
	num_products = get_total_items(request)
	if bag_created or num_products == 0:
		return redirect('bag:bag_view')
	order = None
	login_form = UserLoginForm()
	guest_form = GuestEmailForm()
	delivery = DeliveryTypeForm()
	address_form = AddressCreationForm()
	delivery_address_id = request.session.get('delivery_address_id', None)
	customer_profile, customer_profile_created = Customer.objects.get_or_new(request) 
	address_owner = None
	if customer_profile is not None:
		if request.user.is_authenticated:
			address_owner = Address.objects.filter(customer=customer_profile)
		order = Order.objects.get_or_new(customer_profile, bag)
		if delivery_address_id:
			order.delivery_address = Address.objects.get(id=delivery_address_id)
			del request.session['delivery_address_id']
			order.save()
	if order and order.is_complete:
		if order.delivery_address:
			city = order.delivery_address.city
			if city.lower() == 'nairobi':
				rate = 200
			else:
				rate = 300
			order.delivery_total = _Decimal(rate)		
			order.total = order.update_total()
			order.save()
	uri = request.build_absolute_uri()
	context = {
		'title': 'Checkout',
		'address_owner': address_owner,
		'address_form': address_form,
		'bag': bag,
		'bag_items': bag_items,
		'customer_profile': customer_profile,
		'delivery': delivery,
		'guest_form': guest_form,
		'login_form': login_form,
		'num_products': num_products,
		'order': order,
		'uri': uri,
	}
	return render(request, template_name, context)
	
def checkout_delivery(request):
    if request.method == 'POST':
        delivery = DeliveryTypeForm(request.POST)
        next = request.POST.get('next')
        if delivery.is_valid():
            customer_profile, customer_profile_created = Customer.objects.get_or_new(request)
            if customer_profile is not None:
                bag, bag_created  = Bag.objects.bag_id(request)
                order = Order.objects.get_or_new(customer_profile, bag)
                delivery_type = delivery.cleaned_data['delivery_choices']
                order.delivery = delivery_type
                if delivery_type == '1':
                    order.is_complete = True
                order.save()
                msg = 'Delivery type saved'
                if is_safe_url(next, request.get_host()):
                    return redirect(next)
        else:
            delivery.add_error(None, "Something's wrong, check your values.")

def checkout_address_create(request):
	form = AddressCreationForm(request.POST or None)
	next = request.POST.get('next')
	if form.is_valid():
		address_form = form.save(commit=False)
		bag, bag_created  = Bag.objects.bag_id(request)
		customer_profile, customer_profile_created = Customer.objects.get_or_new(request)
		order = Order.objects.get_or_new(customer_profile, bag)
		city_name = form.cleaned_data['city']
		order.is_complete = True
		order.save()
		if customer_profile is not None:
			address_type = request.POST.get('address_type', 'delivery')
			address_form.address_type = address_type
			address_form.customer = customer_profile
			address_form.save()
			request.session[address_type + '_address_id'] = address_form.id
		else:
			return redirect('checkout:checkout_view')
		if is_safe_url(next, request.get_host()):
			return redirect(next)
	else:
		form.add_error(None, "Something's wrong, check your values")

def checkout_address_reuse(request):
	if request.user.is_authenticated:
		next = request.POST.get('next')
		address_type = request.POST.get('address_type', 'delivery')
		delivery_address = request.POST.get('delivery_address', None)
		customer_profile, customer_profile_created = Customer.objects.get_or_new(request)
		bag, bag_created  = Bag.objects.bag_id(request)
		order = Order.objects.get_or_new(customer_profile, bag)
		if delivery_address is not None:
			qs = Address.objects.filter(customer=customer_profile, id=delivery_address)
			if qs:
				request.session[address_type + '_address_id'] = delivery_address
				order.is_complete = True
				order.save()
		if is_safe_url(next, request.get_host()):
			return redirect(next)
	return redirect('checkout:checkout_view')
	
def checkout_confirmation(request):
	template_name = 'checkout_confirmation.html'
	uri = request.build_absolute_uri()
	bag, bag_created  = Bag.objects.bag_id(request)
	customer_profile, customer_profile_created = Customer.objects.get_or_new(request)
	order = None
	if customer_profile is not None:
		order = Order.objects.get_or_new(customer_profile, bag)
		bag_items = get_bag_items(request)
		num_products = get_total_items(request)
	mpesa_phonenumber = MpesaPhoneNumberForm()
	context = {
		'title': 'Checkout Confirmation',
		'customer_profile': customer_profile,
		'order': order,
		'bag_items': bag_items,
		'num_products': num_products,
		'uri': uri,
		'mpesa_phonenumber': mpesa_phonenumber,
	}
	return render(request, template_name, context)
	
def mpesa_handler(request):
	next = request.POST.get('next')
	phone_number = request.POST.get('mpesa_phonenumber')
	bag, bag_created  = Bag.objects.bag_id(request)
	customer_profile, customer_profile_created = Customer.objects.get_or_new(request)
	started = False
	if customer_profile is not None:
		order = Order.objects.get_or_new(customer_profile, bag)
		total = order.total
		
		
		return redirect('checkout:checkout_success')
	
def checkout_success(request):
	bag, bag_created  = Bag.objects.bag_id(request)
	customer_profile, customer_profile_created = Customer.objects.get_or_new(request)
	order = Order.objects.get_or_new(customer_profile, bag)
	if not order.is_complete:
		redirect('checkout:checkout_view')
	order.mark_paid()
	bag_items = get_bag_items(request)
	items = []
	if bag_items:
		for p in bag_items:
			product_purchase, created = ProductPurchase.objects.get_or_create(
				order_id = order.order_id,
				customer = customer_profile,
				product = p,
				store = p.product.store,
				quantity = p.quantity,
				price = p.total()
			)
			product_purchase.save()
			items.append(p.product.name + ' ( '+str(p.quantity)+' )')
	str_item = ''
	for item in items:
		str_item += item + '\n'
	order.send_customer_mail(customer_profile, str_item)
	order.checkout(request)
	template_name = 'checkout_success.html'
	context = {
		'title': 'Checkout Success',
		'customer_profile': customer_profile,
	}
	return render(request, template_name, context)
	
	