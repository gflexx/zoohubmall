from django.contrib import admin

from .models import *

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'status', 'delivery_total', 'total', 'is_active', 'created_at')
    search_fields = ['order_id']
    list_display_links = ('order_id','customer', 'status', 'is_active',)
    ordering = ['-created_at']

    class Meta:
        model = Order

class ProductPurchaseAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'product', 'store', 'refunded', 'price', 'created_at')
    search_fields = ['order_id', ]
    ordering = ['-created_at']

    class Meta:
        model = ProductPurchase
        
admin.site.register(Order, OrderAdmin)
admin.site.register(ProductPurchase, ProductPurchaseAdmin)
