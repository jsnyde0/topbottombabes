from django.db import models
from django.db.models import Q
from django.utils.text import slugify
from django.urls import reverse

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
    

class ProductQuerySet(models.QuerySet):
    def filter_by_params(self, **params):
        """
        Filter products based on the provided parameters.
        
        :param params: A dictionary of filter parameters
        :return: A filtered queryset
        """
        filters = Q()
        for key, values in params.items():
            if not isinstance(values, list):
                values = [values]  # Convert single values to a list
            
            q_objects = Q()
            for value in values:
                if key == 'category':
                    q_objects |= Q(category__slug=value)
                elif key == 'purpose':
                    q_objects |= Q(purpose__slug=value)
                elif key == 'material':
                    q_objects |= Q(material__slug=value)
                elif key == 'body_part':
                    q_objects |= Q(body_parts__slug=value)
            
            filters &= q_objects
        
        return self.filter(filters)

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

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:view_product", kwargs={"slug": self.slug})
    