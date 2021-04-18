from django.db import models

from users.models import Customer

ADDRESS_TYPE = (
    ('billing', 'Billing'),
    ('delivery', 'Delivery'),
)

class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    address_type = models.CharField(max_length=9, choices=ADDRESS_TYPE)
    country = models.CharField(max_length=252, default='Kenya')
    city = models.CharField(max_length=252)
    locale = models.CharField(max_length=252)
    pick_point = models.CharField(max_length=252)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'addresses'
        ordering = ['city']
        verbose_name_plural = 'Addresses'
    
    def __str__(self):
        return str(self.customer)
        