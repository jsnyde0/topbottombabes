from django.db import models, transaction
from django.contrib.auth.models import User
from a_products.models import Product
from django.urls import reverse
import uuid

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ensure that each authenticated user can only have one cart, while still allowing multiple carts without users (for anonymous users)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(user__isnull=False),
                name='unique_user_cart'
            )
        ]

    @classmethod
    def get_or_create_from_request(cls, request):
        """
        Get an existing cart or create a new one for the given request.

        This method ensures that every request has an associated cart, whether the user
        is authenticated or not. It prioritizes finding existing carts for authenticated users.

        Args:
            cls: The Cart class (passed implicitly as this is a class method).
            request: The HTTP request object.

        Returns:
            A tuple (Cart, bool) where the boolean indicates whether a new cart was created.
        """
        # Ensure the session exists
        if not request.session.session_key:
            request.session.create()

        with transaction.atomic():
            # For authenticated users, return their existing cart or create a new one
            if request.user.is_authenticated:
                try:
                    cart = cls.objects.get(user=request.user)
                    created = False
                except cls.DoesNotExist:
                    cart = cls.objects.create(user=request.user)
                    created = True
            # For anonymous users, get cart by session key or create a new cart
            else:
                cart_id = request.session.get('cart_id')
                if cart_id:
                    try:
                        cart = cls.objects.get(id=cart_id, user__isnull=True)
                        created = False
                    except cls.DoesNotExist:
                        cart = cls.objects.create()
                        created = True
                else:
                    cart = cls.objects.create()
                    created = True

        # Update the session with the cart ID
        session_cart_id = request.session.get('cart_id')
        if not session_cart_id or session_cart_id != cart.id:
            request.session['cart_id'] = cart.id
            request.session.modified = True

        return cart, created

    def __str__(self):
        return f"{self.user}'s cart {self.id}" if self.user else f"Anonymous cart {self.id}"

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

    def merge_with(self, other_cart):
        for item in other_cart.items.all():
            self.add_product(item.product, item.quantity)

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