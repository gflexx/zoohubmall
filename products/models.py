from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.urls import reverse
from django.db.models import Q
from django.db import models
import random

from .utils import unique_slug_generator

# file uploads        
def product_media_upload(instance, filename):
	return 'products_media/{0}/{1}'.format(instance.product.slug, filename)
        
def product_image_upload(instance, filename):
	return 'products/{0}/{1}'.format(instance.slug, filename)
	
def category_image_upload(instance, filename):
	return 'categories/{0}/{1}'.format(instance.slug, filename)
	
class Category(models.Model):
    name = models.CharField(max_length=252)
    slug = models.CharField(blank=True, max_length=252)
    description = models.CharField(max_length=252)
    image = models.ImageField(upload_to=category_image_upload)
    views = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        ordering = ['-created_at']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:category_view', kwargs={'slug': self.slug})

class Store(models.Model):
    owner = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=252, unique=True)
    slug = models.CharField(blank=True, max_length=252)
    description = models.TextField(blank=True)
    views = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stores'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:store_view', kwargs={'slug': self.slug})
        
    def verify(self):
    	self.verified = True
    	self.save()
        
class ProductQueryset(models.QuerySet):
    def get_random(self):
        max_id = self.model.objects.all().aggregate(max_id=max('id'))['max_id']
        while True:
            pk = random.randint(1, max_id)
            products = self.model.objects.filter(pk=pk)
        return products

    def is_active(self):
        return self.filter(Q(is_active=True) & Q(quantity__gt=0))

    def recommended(self):
        return self.is_active().filter(is_recommended=True)

    def bestseller(self):
        return self.is_active().filter(is_bestseller=True)

    def featured(self):
        return self.is_active().filter(is_featured=True)

class Product(models.Model):
    name = models.CharField(max_length=252)
    slug = models.CharField(blank=True, max_length=252)
    image = models.ImageField(upload_to=product_image_upload)
    description = models.TextField()
    brand = models.CharField(max_length=252, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    views = models.IntegerField(default=1)
    is_digital = models.BooleanField(default=False)
    old_price = models.DecimalField(max_digits=9, decimal_places=1, blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=1)
    category = models.ManyToManyField(Category)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True)
    has_extra_data = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ProductQueryset.as_manager()

    class Meta:
        db_table = 'products'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.name
	
    def get_absolute_url(self):
        return reverse('products:product_view', kwargs={'slug': self.slug})
        
class Comment(models.Model):
    posted_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True)
    text = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def disapprove(self):
        self.is_approved = False
        self.save()

    def __str__(self):
        return '{}'.format(self.posted_by.email)

class Review(models.Model):
    posted_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True)
    text = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def dis_approve(self):
        self.is_approved = False
        self.save()

    def __str__(self):
        return '{}'.format(self.posted_by.email)
        
class Rating(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True)
	rated_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True)
	stars = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
	created_at = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return '{}'.format(self.product.name)
        
class ProductMedia(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True)
	media = models.FileField(upload_to=product_media_upload, null=True, blank=True)
	
	def __str__(self):
		return '{}'.format(self.media)

# model slug signals
def product_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

def category_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

def store_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(product_slug, sender=Product)
pre_save.connect(store_slug, sender=Store)
pre_save.connect(category_slug, sender=Category)
