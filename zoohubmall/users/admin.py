from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib import admin

from .models import *

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'is_admin')
    list_filter = ('is_admin',)
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_admin',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )

class GuestAdmin(admin.ModelAdmin):
    list_display = ('email', 'created')
    search_fields = ('email',)
    
    class Meta:
        model = Guest

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', 'created', 'account_type')

    class Meta:
        model = Customer

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Guest, GuestAdmin)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
