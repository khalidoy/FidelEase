from django import forms
from .models import Product,Gift

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'description', 'image']
        

class GiftForm(forms.ModelForm):
    class Meta:
        model = Gift
        fields = ['productId', 'pointCost']