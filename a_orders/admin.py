from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('name', 'description', 'price', 'total_price')

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