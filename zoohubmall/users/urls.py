from django.conf.urls import url

from .views import *

app_name = 'users'

urlpatterns = [
    url(r'^dashboard/$', dashboard, name='dashboard'),
    url(r'^create_store/$', create_store, name='create_store'),
    url(r'^customer_profile_creation/$', customer_profile_creation, name='customer_profile_creation'),
    url(r'^custom_login/$', custom_login, name='custom_login'),
    url(r'^profile/$', profile, name='profile'),
    url(r'^orders_view/$', orders_view, name='orders_view'),
    url(r'^guest_register/$', guest_register, name='guest_register'),
    url(r'^purchase_history/$', purchase_history, name='purchase_history'),
    
    url(r'^store/api/chart_api/$', chart_api, name='chart_api'),
    url(r'^store/add_product/$', add_product, name='add_product'),
	url(r'^store/all_products/$', all_products, name='all_products'),
	url(r'^store/delete_product/(?P<slug>[\w_-]+)/$', delete_product, name='delete_product'),
	url(r'^store/delete_store/(?P<slug>[\w_-]+)/$', delete_store, name='delete_store'),
	url(r'^store/metrics/$', metrics, name='metrics'),
    url(r'^store/stock/$', stock, name='stock'),
    url(r'^store/store_orders/$', store_orders, name='store_orders'),
    url(r'^store/update_product/(?P<slug>[\w_-]+)/$', update_product, name='update_product'),
    url(r'^store/update_store/$', update_store, name='update_store'),
    
    url(r'^update_user/$', update_user, name='update_user'),
]
