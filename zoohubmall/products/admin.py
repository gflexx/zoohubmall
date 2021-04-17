from django.contrib.admin import AdminSite
from django.contrib import admin

from . import models

AdminSite.site_title = 'zooHubMall Admin'
AdminSite.site_header = 'zooHubMall Admin Panel'

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'uploaded_at', 'updated_at', 'is_recommended', 'is_bestseller', 'is_featured', 'is_active')
    list_display_links = ('name', 'is_bestseller', 'is_featured', 'is_active')
    list_per_page = 50
    ordering = ['uploaded_at']
    search_fields = ['name', 'description']

    class Meta:
        model = models.Product

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ['name',]
    class Meta:
        model = models.Category

class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_featured', 'updated_at')
    list_display_links = ('name', 'is_featured')
    search_fields = ['name', 'description']

    class Meta:
        model = models.Store

admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Store, StoreAdmin)
admin.site.register(models.Comment)
admin.site.register(models.Review)
admin.site.register(models.Rating)

