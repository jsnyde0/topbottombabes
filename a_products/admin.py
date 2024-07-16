from django.contrib import admin
from .models import Product, Category, Purpose, Material, BodyPart, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    readonly_fields = ('slug',)

@admin.register(Purpose)
class PurposeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    readonly_fields = ('slug',)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    readonly_fields = ('slug',)

@admin.register(BodyPart)
class BodyPartAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    readonly_fields = ('slug',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'is_primary', 'is_secondary')
    list_filter = ('is_primary', 'is_secondary', 'product')
    search_fields = ('product__name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'material')
    list_filter = ('category', 'material', 'purpose', 'body_parts')
    search_fields = ('name', 'description')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    filter_horizontal = ('purpose', 'body_parts')