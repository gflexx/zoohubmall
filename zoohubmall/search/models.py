from django.contrib.auth import get_user_model
from django.db import models

class SearchItem(models.Model):
	search = models.CharField(max_length=252)
	ip = models.CharField(max_length=12)
	time = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.search
