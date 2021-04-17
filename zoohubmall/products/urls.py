from django.conf.urls import url

from .views import *

app_name = 'products'

urlpatterns = [
	url(r'^categories/$', categories, name='categories'),
	url(r'^category/(?P<slug>[\w_-]+)/$', category_view, name='category_view'),
	url(r'^products/(?P<slug>[\w_-]+)/$', product_view, name='product_view'),
	url(r'^product/comments/$', product_comment, name='product_comment'),
	url(r'^store/(?P<slug>[\w_-]+)/$', store_view, name='store_view'),
	url(r'^stores/$', stores, name='stores'),
]
