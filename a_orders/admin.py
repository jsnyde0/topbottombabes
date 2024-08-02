from django.contrib import admin
from django import forms
from .models import Order, OrderItem, Address
from a_products.models import Product

class ProductModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj}"

class OrderItemInlineForm(forms.ModelForm):
    product = ProductModelChoiceField(
        queryset=Product.objects.all(),
        widget=admin.widgets.AutocompleteSelect(
            OrderItem._meta.get_field('product'),
            admin.site,
            attrs={'data-placeholder': 'Start typing to search products...'}
        )
    )

    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = OrderItemInlineForm
    extra = 0
    readonly_fields = ('name', 'description', 'price', 'total_price')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            return self.form.base_fields['product']
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_price', 'created_at', 'email', 'phone', 'payment_status', 'payment_amount')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user', 'user__email', 'email', 'phone', 'payment_intent_id')
    readonly_fields = ('order_number', 'user', 'created_at', 'updated_at', 'total_price', 'payment_status', 'payment_intent_id', 'payment_amount')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'total_price')
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'payment_intent_id', 'payment_amount')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'marketing_consent')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'estimated_delivery')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address',)
        }),
        ('Billing Information', {
            'fields': ('billing_address',),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'tracking_number')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price')
    list_filter = ('order__status', 'created_at')
    search_fields = ('order__order_number', 'product__name', 'name')
    readonly_fields = ('name', 'description', 'price', 'total_price')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'street', 'city', 'state', 'country', 'zip_code', 'default')
    list_filter = ('type', 'country', 'default')
    search_fields = ('user__username', 'street', 'city', 'state', 'country', 'zip_code')
    raw_id_fields = ('user',)
    list_editable = ('default',)

    fieldsets = (
        (None, {
            'fields': ('user', 'type', 'default')
        }),
        ('Address Details', {
            'fields': ('street', 'city', 'state', 'country', 'zip_code')
        }),
    )