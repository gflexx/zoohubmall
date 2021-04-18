from django.conf.urls import url

from .views import *

app_name = 'bag'

urlpatterns = [
    url(r'^$', bag_view, name='bag_view'),
    url(r'^add_to_cart/$', add_to_bag, name='add_to_bag'),
    url(r'^update_item_quantity/$', update_item_quantity, name='update_item_quantity'),
    url(r'^remove_from_bag/$', remove_from_bag, name='remove_from_bag'),
] 
