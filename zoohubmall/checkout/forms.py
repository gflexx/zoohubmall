from django import forms

from addresses.models import Address

class AddressCreationForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('city', 'locale', 'pick_point', )

DELIVERY = (
    (2, 'Yes, Deliver to me'),
    (1, 'No Delivery, ill pick them myself'),
)

class DeliveryTypeForm(forms.Form):
    delivery_choices = forms.ChoiceField(choices=DELIVERY, required=True)

class MpesaPhoneNumberForm(forms.Form):
    phone_number = forms.CharField()
