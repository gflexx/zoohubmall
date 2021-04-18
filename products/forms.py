from django import forms

from .models import *

class StoreCreationForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

    class Meta:
        model = Store
        fields = ('name', 'description', )

class StoreUpdateForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

    class Meta:
        model = Store
        fields = ('name', 'description', )

class ProductCreationForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Product
        fields = ('name', 'price', 'quantity', 'image', 'description', 'category')

    def clean_price(self):
        def process_price(price):
            tp = (price*105)/100
            return tp
        set_price = self.cleaned_data.get('price')
        price = process_price(set_price)
        return price

class ProductUpdateForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    is_active = forms.BooleanField(help_text='Active products are displayed to buyers, inactive ones are hidden.', required=False)

    class Meta:
        model = Product
        fields = ('name', 'price', 'quantity', 'image', 'description', 'is_active')

class CommentCreationForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='')

    class Meta:
        model = Comment
        fields = ('text', )

class ReviewCreationForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='')

    class Meta:
        model = Review
        fields = ('text', )

class RatingCreationForm(forms.ModelForm):
	class Meta:
		model = Rating
		fields = ('stars', )

class ProductMediaCreationForm(forms.ModelForm):
    class Meta:
        model = ProductMedia
        fields = ('media', )
