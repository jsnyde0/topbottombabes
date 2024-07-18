from django.db import models, transaction
from django.contrib.auth.models import User
from a_products.models import Product
from django.urls import reverse
import uuid

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'session_key'],
                name='unique_user_session_cart'
            )
        ]

    @classmethod
    def get_or_create_cart(cls, request):
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
            if request.user.is_authenticated:
                # For authenticated users, first try to get their existing cart
                cart = cls.objects.filter(user=request.user).first()
                created = False
                if cart:
                    # If we found an existing cart, update its session key
                    cart.session_key = request.session.session_key
                    cart.save()
            else:
                # For anonymous users, try to get cart by session key or create a new one
                cart_id = request.session.get('cart_id')
                if cart_id:
                    try:
                        cart = cls.objects.get(id=cart_id, user__isnull=True)
                        created = False
                    except cls.DoesNotExist:
                        cart = cls.objects.create(session_key=request.session.session_key)
                        created = True
                else:
                    cart = cls.objects.create(session_key=request.session.session_key)
                    created = True

        # Always update the session with the cart ID
        request.session['cart_id'] = cart.id
        request.session.modified = True
        return cart, created

    def __str__(self):
        return f"{self.user.username}'s cart" if self.user else f"cart {self.session_key}"

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