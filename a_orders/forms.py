from django import forms
from .models import Order, Address

class ContactForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['email', 'phone', 'marketing_consent']
        labels = {
            'marketing_consent': 'I agree to receive marketing emails',
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'street', 'city', 'state', 'country', 'zip_code']
        labels = {
            'zip_code': 'ZIP Code'
        }

class ShippingForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'street', 'zip_code', 'city', 'state', 'country']
        labels = {
            'zip_code': 'ZIP Code'
        }

class PaymentForm(forms.ModelForm):
    use_shipping_address = forms.BooleanField(required=False, initial=True, label='Use shipping address as billing address')

    class Meta:
        model = Order
        fields = ['payment_method']
        # widgets = {
        #     'use_shipping_address': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.billing_address_form = AddressForm(prefix='billing')
        self.fields.update(self.billing_address_form.fields)

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('use_shipping_address'):
            billing_form = AddressForm(self.data, prefix='billing')
            if billing_form.is_valid():
                cleaned_data.update(billing_form.cleaned_data)
            else:
                for field, errors in billing_form.errors.items():
                    for error in errors:
                        self.add_error(f'billing-{field}', error)
        return cleaned_data