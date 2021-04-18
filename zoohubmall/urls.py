from django.conf.urls.static import static
from django.conf.urls import url
from django.conf import settings
from django.contrib import admin
from django.urls import include

from bag.views import bag_update_api

urlpatterns = [
	url(r'^', include('core.urls'), name='core'),
	url(r'^admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    url(r'^adxtry23nhj/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/', include('users.urls'), name='users'),
    url(r'^api/bag/', bag_update_api, name='bag_api'),
    url(r'^bag/', include('bag.urls'), name='bag'),
    url(r'^catalog/', include('products.urls'), name='products'),
    url(r'^search/', include('search.urls'), name='search'), 
    url(r'^checkout/', include('checkout.urls'), name='checkout'),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL,)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    