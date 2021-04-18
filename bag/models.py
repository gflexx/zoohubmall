from django.contrib.auth import get_user_model
from decimal import Decimal as _Decimal
from django.db import models
import random

from products.models import Product

class BagManager(models.Manager):
    def check_owner(self, request):
        _bag = Bag.objects.filter(owner=request.user, checked_out=False).order_by('-date_added')
        bag = _bag.first()
        return bag

    def bag_id(self, request):
        bag_id = request.session.get('bag_id', None)
        if bag_id == None:
            is_new = True
            id = Bag.objects.generate_bag_id()
            bag = Bag.objects.create(bag_identity=id)
            request.session['bag_id'] = id
        else:
            is_new = False
            bag = Bag.objects.get(bag_identity=bag_id)
            if bag.owner is None and request.user.is_authenticated:
                bag.owner = request.user
                bag.save()
        return bag, is_new

    def generate_bag_id(self):
        bag_id = ''
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()'
        length = 50
        for x in range(length):
            bag_id += chars[random.randint(0, len(chars)-1)]
        return bag_id


class Bag(models.Model):
    bag_identity = models.CharField(max_length=50)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True)
    checked_out = models.BooleanField(default=False)
    total = models.DecimalField(default=0.0, max_digits=12, decimal_places=1)
    date_added = models.DateTimeField(auto_now_add=True)

    objects = BagManager()

    def __str__(self):
        return str(self.bag_identity)


class BagItem(models.Model):
    bag = models.ForeignKey(Bag, on_delete=models.CASCADE, default=1)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(default=0.0, max_digits=9, decimal_places=1)
    date_added = models.DateTimeField(auto_now_add=True)

    def auto_add_quantity(self, quantity):
        self.quantity = self.quantity + int(quantity)
        self.save()

    def total(self):
        return _Decimal(self.quantity * self.product.price)

    def __str__(self):
        return self.product.name
