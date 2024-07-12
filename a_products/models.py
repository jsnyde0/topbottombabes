from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True, editable=False)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"

class Purpose(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True, editable=False)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True, editable=False)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class BodyPart(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True, editable=False)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, unique=True, editable=False)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    purpose = models.ManyToManyField(Purpose, blank=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    body_parts = models.ManyToManyField(BodyPart, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)