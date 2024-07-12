from django.contrib import admin
from .models import Product, Category, Purpose, Material, BodyPart


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'material')
    list_filter = ('category', 'material', 'purpose', 'body_parts')
    search_fields = ('name', 'description')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    filter_horizontal = ('purpose', 'body_parts')

admin.site.register(Category)
admin.site.register(Purpose)
admin.site.register(Material)
admin.site.register(BodyPart)