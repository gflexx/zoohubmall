from django.db.models.signals import pre_save, post_save
from decimal import Decimal as _Decimal
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.db import models

from .utils import generate_order_id
from addresses.models import Address
from bag.models import Bag, BagItem
from bag.views import get_bag_items
from checkout.signals import purchased_product_signal
from products.models import Product, Store
from users.models import Customer

ORDER_STATUS = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('delivered', 'Delivered'),
    ('refund', 'Refund'),
)

DELIVERY = (
    (1, 'No Delivery, ill pick them myself'),
    (2, 'Yes, Deliver to me'),
)

class OrderManager(models.Manager):
    def get_or_new(self, customer_profile, bag):
        order_qs = self.get_queryset().filter(customer=customer_profile,  bag=bag, is_active=True)
        if order_qs:
            order = order_qs.first()
        else:
            order = self.model.objects.create(customer=customer_profile, bag=bag)
        return order

class Order(models.Model):
    order_id = models.CharField(max_length=36, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    gift_recipient = models.CharField(max_length=252, null=True)
    bag = models.ForeignKey(Bag, on_delete=models.SET_NULL, blank=True, null=True)
    delivery = models.CharField(max_length=1, choices=DELIVERY, null=True)
    delivery_address = models.ForeignKey(Address, related_name='delivery_address', on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=9, default='created', choices=ORDER_STATUS)
    delivery_total = models.DecimalField(default=0.0, max_digits=9, decimal_places=1)
    total = models.DecimalField(default=0.0, max_digits=12, decimal_places=1)
    is_complete = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    checked_out = models.BooleanField(default=False)
    sent_email = models.BooleanField(default=False)

    objects = OrderManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Orders'

    def __str__(self):
        return self.order_id

    def update_total(self):
        bag_total = self.bag.total
        delivery_total = self.delivery_total
        totals = _Decimal(bag_total)+_Decimal(delivery_total)
        self.total = totals
        self.save()
        return totals

    def mark_paid(self):
        if self.status != 'paid':
            if self.is_complete:
                self.status = 'paid'
                self.save()
        return self.status

    def send_customer_mail(self, customer_profile, str_item):
        if self.status == 'paid':
            if not self.sent_email:
                mall_email = settings.EMAIL_HOST_USER
                customer_mail = customer_profile.email
                subject = 'Checkout confirmation'
                message = 'Your orders are being processed for Order ID: '+self.order_id+'\nFor the purchase of: \n'+str_item
                send_mail(subject, message, mall_email, [customer_mail], fail_silently=True)
                self.sent_email = True
                self.save()
            return self.sent_email

    def checkout(self, request):
        if not self.checked_out:
            if self.status == 'paid':
                self.checked_out = True
                bag, bag_created  = Bag.objects.bag_id(request)
                bag.checked_out = True
                bag.save()
                del request.session['bag_id']
                del request.session['num_products']
                self.save()
                msg = 'A purchase confirmation email has been sent you.'
                messages.success(request, msg)
        return self.checked_out

class ProductPurchaseManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(refunded=False)

class ProductPurchase(models.Model):
    order_id = models.CharField(max_length=36, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(BagItem, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(default=0.0, max_digits=12, decimal_places=1)
    quantity = models.PositiveIntegerField()
    refunded = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ProductPurchaseManager()

    class Meta:
        db_table = 'purchased_product'
        ordering = ['-created_at']

    def __str__(self):
        return self.product.product.name

def create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = generate_order_id(instance)

    older_orders = Order.objects.filter(bag=instance.bag).exclude(customer=instance.customer)
    if older_orders.exists():
        older_orders.update(is_active=False)

def bag_total_change(sender, instance, created, *args, **kwargs):
    if not created:
        bag = instance
        bag_total = bag.total
        bag_id = bag.id
        qs = Order.objects.filter(bag__id=bag_id)
        if qs:
            order = qs.first()
            order.update_total()

def order_post_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()
        
def update_product_quantity(sender, instance, created, *args, **kwargs):
	if created:
		item = instance
		quantity = instance.quantity
		product = Product.objects.get(slug=instance.product.product.slug)
		product.quantity = (product.quantity - quantity)
		product.save()

post_save.connect(update_product_quantity, sender=ProductPurchase)
post_save.connect(order_post_save, sender=Order)
post_save.connect(bag_total_change, sender=Bag)
pre_save.connect(create_order_id, sender=Order)  
    
    
