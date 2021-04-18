from django.conf.urls import url

from .views import *

app_name = 'core'

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^about/$', about, name='about'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^help/$', help, name='help'),
    url(r'^privacy/$', privacy, name='privacy'),
    url(r'^terms/$', terms, name='terms'),
]
