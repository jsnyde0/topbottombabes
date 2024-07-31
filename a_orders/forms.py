from django import forms
from .models import Order, Address

class ContactForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['email', 'phone', 'marketing_consent']

class ShippingForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'country', 'zip_code']
        labels = {
            'zip_code': 'ZIP Code'
        }

class PaymentForm(forms.ModelForm):
    use_shipping_address = forms.BooleanField(required=False, initial=True, label='Use shipping address as billing address')

    class Meta:
        model = Order
        fields = ['payment_method']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['billing_address'] = ShippingForm()
        self.fields['billing_address'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('use_shipping_address') and not cleaned_data.get('billing_address'):
            raise forms.ValidationError("Please provide a billing address or use the shipping address.")
        return cleaned_data