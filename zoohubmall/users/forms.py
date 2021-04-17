from django.contrib.auth import get_user_model
from django import forms

from .models import Customer

class UserUpdateForm(forms.ModelForm):
    image = forms.ImageField(label='Update Profile Picture')
    
    class Meta:
        model = get_user_model()
        fields = ('full_name', 'email', 'phone_number', 'image')

class CustomerSelectionForm(forms.ModelForm):
    
    class Meta:
    	model = Customer
    	fields = ('account_type', )

class GuestEmailForm(forms.Form):
    email = forms.EmailField(
    	widget = forms.TextInput(
    		attrs={'placeholder': 'Email'}
    	)
    )

class UserLoginForm(forms.Form):
    email = forms.CharField(
        label='Email',
        widget=forms.TextInput(
            attrs={'placeholder': 'Email'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder': '* * * * * * *'}
        )
    )
