from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages

from .models import *
from products.models import Product

def get_bag_items(request):
    bag, is_new = Bag.objects.bag_id(request)
    return BagItem.objects.filter(bag=bag)

def get_total(request):
    bag_items = get_bag_items(request)
    total = sum([item.total() for item in bag_items])
    return total

def update_bag_total(request):
    bag, is_new = Bag.objects.bag_id(request)
    bag.total = get_total(request)
    bag.save()

def get_total_items(request):
    bag_items = get_bag_items(request)
    total_items = sum([item.quantity for item in bag_items])
    return total_items


def bag_view(request):
    template_name = 'bag.html'
    bag, is_new = Bag.objects.bag_id(request)
    bag_products = bag.products.all()
    bag_items = get_bag_items(request)
    total_quantity = get_total_items(request)
    request.session['num_products'] = total_quantity
    total = bag.total
    context = {
        'title': 'Shopping Bag',
        'bag_products': bag_products,
        'bag_items': bag_items,
        'bag': bag,
        'total': total,
    }
    return render(request, template_name, context)


def add_to_bag(request):
    product_slug = request.POST.get('product_slug')
    if product_slug is not None:
        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            msg = 'Sorry the product nolonger exists'
            messages.success(request, msg)
            return redirect('bag:bag_view')
        bag, is_new = Bag.objects.bag_id(request)
        quantity = request.POST.get('quantity', 1)
        added = False
        excess = False
        bag_items = get_bag_items(request)
        for item in bag_items:
            if item.product.id == product.id:
                if item.quantity >= product.quantity:
                    excess = True
                    message = 'The number is too high, only '+str(product.quantity)+' remaining'
                else:
                    item.auto_add_quantity(quantity)
                    message = 'Quantity updated'
                    added = True
        if not added and not excess:
            bag.products.add(product)
            bag_item = BagItem()
            bag_item.bag = bag
            bag_item.product = product
            bag_item.save()
            message = 'Item added to bag.'
            added = True
        msg = 'added to shopping bag'
        total_quantity = get_total_items(request)
        request.session['num_products'] = total_quantity
        update_bag_total(request)
        total = get_total(request)
        if request.is_ajax():
            data = {
                'added': added,
                'numProducts': total_quantity,
                'total': total,
                'messageLoad': message,
            }
            return JsonResponse(data)
    return redirect('bag:bag_view')


def remove_from_bag(request):
    product_slug = request.POST.get('product_slug')
    if product_slug is not None:
        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            msg = 'Sorry product no longer exists'
            return redirect('bag:bag_view')
        bag, is_new = Bag.objects.bag_id(request)
        bag_items = BagItem.objects.filter(bag=bag)
        item = bag_items.filter(product=product)
        item.delete()
        bag.products.remove(product)
        removed = True
        msg = 'Item removed from shopping bag'
        total_quantity = get_total_items(request)
        request.session['num_products'] = total_quantity
        update_bag_total(request)
        total = get_total(request)
        if request.is_ajax():
            data = {
                'removed': removed,
                'numProducts': total_quantity,
                'total': total,
                'productSlug': product.slug,
                'messageLoad': msg,
            }
            return JsonResponse(data)
    return redirect('bag:bag_view')
    

def update_item_quantity(request):
    product_slug = request.POST.get('product_slug')
    if product_slug is not None:
        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            msg = 'Sorry product no longer exists'
            messages.success(request, msg)
            return redirect('bag:bag_view')
        quantity = request.POST.get('quantity')
        bag_items = get_bag_items(request)
        for item in bag_items:
            if item.product.id == product.id:
                if int(quantity) <= product.quantity:
                    item.quantity = int(quantity)
                    item.save()
                    total_item_price = item.total()
                    msg = 'Quantity updated'
                else:
                    quantity = product.quantity
                    item.quantity = quantity
                    item.save()
                    total_item_price = item.total()
                    msg = 'The number you entered for '+str(product.name)+' was too high, only '+str(quantity)+' remaining'
        total_quantity = get_total_items(request)
        request.session['num_products'] = total_quantity
        update_bag_total(request)
        total = get_total(request)
        if request.is_ajax():
            data = {
                'numProducts': total_quantity,
                'totalItemPrice': total_item_price,
                'total': total,
                'messageLoad': msg,
            }
            return JsonResponse(data)
    return redirect('bag:bag_view')

def bag_update_api(request):
    bag, is_new = Bag.objects.bag_id(request)
    items = bag.products.all()
    products = [{'image':x.image.url, 'name':x.name, 'quantity':x.quantity, 'price':x.price} for x in items]
    bag_data = {'products': products, 'total':bag.total}
    return JsonResponse(bag_data)
