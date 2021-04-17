from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.db import models
from django.utils import timezone

from .signals import object_viewed_signal
from .utils import get_client_ip

class ObjectViewed(models.Model):
	user_email = models.EmailField(null=True, blank=True)
	ip_address = models.CharField(max_length=18, null=True, blank=True)
	content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	timestamp = models.DateTimeField()
	
	def __str__(self):
		return '{} viewed at {}'.format(self.content_object, self.timestamp)
		
	class Meta:
		ordering = ['-timestamp']
		verbose_name = 'Object Viewed'
		verbose_name_plural = 'Objects Viewed'

def object_viewed_receiver(sender, instance, request, *args, **kwargs):
	c_type = ContentType.objects.get_for_model(sender)
	user_mail = None
	if request.user.is_authenticated:
		user_mail = request.user.email
	ObjectViewed.objects.create(
		user_email = user_mail,
		ip_address = get_client_ip(request),
		content_type = c_type,
		object_id = instance.id,
		timestamp = timezone.now()
	)

object_viewed_signal.connect(object_viewed_receiver)
