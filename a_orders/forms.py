from django import forms
from django.core.validators import RegexValidator
from .models import Order, Address

class ContactForm(forms.ModelForm):
    phone = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )

    class Meta:
        model = Order
        fields = ['email', 'phone', 'marketing_consent']
        labels = {
            'marketing_consent': 'I agree to receive marketing emails',
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'street', 'zip_code', 'city', 'state', 'country']
        labels = {
            'zip_code': 'ZIP Code'
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_method']