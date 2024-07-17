from django.contrib import admin
from .models import Profile

# Register our Profile model with sensible fields
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'avatar')
    search_fields = ('user', 'email')
    list_filter = ('user', 'email')

admin.site.register(Profile, ProfileAdmin)
