from django.conf.urls import url

app_name = 'search'

from .views import *

urlpatterns = [
	url(r'^$', search_view, name='search_view'),
	url(r'^store_search/$', store_search, name='store_search'),
]
