from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.templatetags.static import static

# Profile class with one-to-one relationship to User model, with avatar image, name, address, phone number, email, and bio
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True, null=True)

    def __str__(self):
        return self.name if self.name else self.email

    def get_absolute_url(self):
        return reverse("profiles:view_profile")

    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return static('images/default-avatar.jpg')

    
    