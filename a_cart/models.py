from django.db import models
from django.contrib.auth.models import User
from a_products.models import Product
from django.urls import reverse

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s cart"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_num_items(self):
        return sum(item.quantity for item in self.items.all())

    def get_absolute_url(self):
        return reverse("view_cart")

    def add_product(self, product, quantity=1):
        cart_item, created = self.items.get_or_create(product=product, defaults={'quantity': quantity})
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item

    def update_quantity(self, product_id, quantity):
        cart_item = self.items.get(product_id=product_id)
        cart_item.quantity = quantity
        cart_item.save()

    def remove_product(self, product_id):
        cart_item = self.items.get(product_id=product_id)
        cart_item.delete()
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in {self.cart}"

    def get_total_price(self):
        return self.product.price * self.quantity