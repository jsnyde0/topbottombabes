from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user', 'user__email', 'shipping_address')
    readonly_fields = ('order_number', 'user', 'created_at', 'updated_at', 'total_price')
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

    # def has_delete_permission(self, request, obj=None):
    #     return False  # Prevent deletion of orders

    # def has_add_permission(self, request):
    #     return False  # Prevent adding orders directly from admin