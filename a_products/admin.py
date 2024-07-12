from django.contrib import admin
from .models import Product, Category, Purpose, Material, BodyPart

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

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'material')
    list_filter = ('category', 'material', 'purpose', 'body_parts')
    search_fields = ('name', 'description')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    filter_horizontal = ('purpose', 'body_parts')