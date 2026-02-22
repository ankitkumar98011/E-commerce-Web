from django import forms
from .models import Product, Order



class ProductUploadForm(forms.ModelForm):
    """Form for users to upload products"""
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount_price', 'is_discounted', 'category', 'image', 'quality', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product Name',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Product Description',
                'rows': 5,
                'required': True
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Price (₹)',
                'step': '0.01',
                'required': True
            }),
            'discount_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Discount Price (₹)',
                'step': '0.01',
            }),
            'is_discounted': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category (e.g., Electronics, Accessories)',
                'required': True
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'quality': forms.Select(attrs={
                'class': 'form-control'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Stock Quantity',
                'required': True
            })
        }


class ProductEditForm(forms.ModelForm):
    """Form for sellers to edit their products, including discount"""
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount_price', 'is_discounted', 'category', 'image', 'quality', 'stock', 'warranty_provided', 'warranty_days', 'warranty_terms']


class CheckoutForm(forms.ModelForm):
    """Form for checkout"""
    
    class Meta:
        model = Order
        fields = ['full_name', 'shipping_address', 'city', 'pincode', 'phone_number', 'payment_method']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'required': True
            }),
            'shipping_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your complete shipping address',
                'rows': 4,
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city',
                'required': True
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter 6-digit pincode',
                'pattern': '[0-9]{6}',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'type': 'tel',
                'pattern': '[0-9]{10}',
                'required': True
            }),
            'payment_method': forms.RadioSelect(choices=Order.PAYMENT_METHODS),
        }


class AddToCartForm(forms.Form):
    """Form for adding items to cart"""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=100,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'number'
        })
    )
