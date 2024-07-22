from django.contrib import admin
from django import forms
from .models import Order, OrderItem
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
    list_display = ('order_number', 'user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user', 'user__email', 'shipping_address')
    readonly_fields = ('order_number', 'user', 'created_at', 'updated_at', 'total_price')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'total_price', 'payment_method', 'payment_id')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'estimated_delivery')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_country', 'shipping_zip')
        }),
        ('Billing Information', {
            'fields': ('billing_address', 'billing_city', 'billing_country', 'billing_zip'),
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