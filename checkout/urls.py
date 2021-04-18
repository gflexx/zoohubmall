from django.conf.urls import url

from .views import *

app_name = 'checkout'

urlpatterns = [
	url(r'^$', checkout, name='checkout_view'),
	url(r'^checkout_address_create/$', checkout_address_create, name='checkout_address_create'),
	url(r'^checkout_address_reuse/$', checkout_address_reuse, name='checkout_address_reuse'),
	url(r'^checkout_confirmation/$', checkout_confirmation, name='checkout_confirmation'),
	url(r'^checkout_delivery/$', checkout_delivery, name='checkout_delivery'),
	url(r'^mpesa_handler/$', mpesa_handler, name='mpesa_handler'),
	url(r'^checkout_success/$', checkout_success, name='checkout_success'),
]
