from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at', 'get_num_items', 'get_total_price')
    search_fields = ('user__username',)
    inlines = [CartItemInline]

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'added_at')
    search_fields = ('cart__user__username', 'product__name')

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
