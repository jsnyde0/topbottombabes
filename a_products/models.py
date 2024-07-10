from django.db import models
from django.utils.text import slugify

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, unique=True, editable=False)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)