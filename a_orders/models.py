from django.db import models
from django.db.models import Sum, F
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from a_products.models import Product
from a_cart.models import Cart

class Address(models.Model):
    TYPE_CHOICES = [('SHIPPING', 'Shipping'), ('BILLING', 'Billing')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    default = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'type', 'default']

    def save(self, *args, **kwargs):
        if self.default:
            # Set all other addresses of this type for this user to non-default
            Address.objects.filter(user=self.user, type=self.type).update(default=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_default(cls, user, address_type):
        return cls.objects.filter(user=user, type=address_type, default=True).first()

    @classmethod
    def set_default(cls, address_id, user, address_type):
        cls.objects.filter(user=user, type=address_type).update(default=False)
        cls.objects.filter(id=address_id, user=user, type=address_type).update(default=True)

class Order(models.Model):
    # Status choices
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('RETURNED', 'Returned'),
        ('REFUNDED', 'Refunded'),
        ('COMPLETED', 'Completed'),
    ]

    # Payment method choices
    PAYMENT_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('PAYPAL', 'PayPal'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    order_number = models.CharField(max_length=6, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, null=True, blank=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # For storing payment gateway transaction ID
    
    # Shipping information
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100)
    shipping_zip = models.CharField(max_length=20)

    # Billing information (if different from shipping)
    billing_address = models.TextField(blank=True, null=True)
    billing_city = models.CharField(max_length=100, blank=True, null=True)
    billing_country = models.CharField(max_length=100, blank=True, null=True)
    billing_zip = models.CharField(max_length=20, blank=True, null=True)

    # Additional fields
    notes = models.TextField(blank=True, null=True)  # For customer or admin notes
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"
    
    def compute_total_price(self):
        # if the order has items, compute the total price
        self.total_price = self.items.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or Decimal('0.00')

    def set_order_number(self):
        if self.order_number:
            return
        
        last_order = Order.objects.all().order_by('id').last()
        if not last_order:
            self.order_number = '000001'
        else:
            last_order_number = int(last_order.order_number)
            new_order_number = last_order_number + 1
            self.order_number = f'{new_order_number:06d}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.set_order_number()
        super().save(*args, **kwargs)

        if is_new:
            self.compute_total_price()
            super().save(update_fields=['total_price'])

    def sync_with_cart(self, cart):
        # Clear existing order items
        self.items.all().delete()

        # Add items from cart
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=self,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                name=cart_item.product.name,
                description=cart_item.product.description
            )

        # Recompute total price
        self.compute_total_price()
        self.save(update_fields=['total_price'])

    @classmethod
    def get_or_create_order(cls, request, sync_with_cart=True):
        cart, _ = Cart.get_or_create_cart(request)
        
        
        if request.user.is_authenticated:
            # retrieve any 'pending' order for an authenticated user or create one
            order, created = cls.objects.get_or_create(
                user=request.user,
                status='PENDING',
                defaults={'total_price': Decimal('0.00')}
            )
        else:
            # For anonymous users, we'll use the session to store the order
            order_id = request.session.get('order_id')
            if order_id:
                try:
                    order = cls.objects.get(id=order_id, status='PENDING')
                    created = False
                except cls.DoesNotExist:
                    order = cls.objects.create(status='PENDING', total_price=Decimal('0.00'))
                    created = True
            else:
                order = cls.objects.create(status='PENDING', total_price=Decimal('0.00'))
                created = True
            
            request.session['order_id'] = order.id

        # sync the order with the cart
        if sync_with_cart:
            order.sync_with_cart(cart)

        return order
    




class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Additional fields
    name = models.CharField(max_length=255, blank=True, null=False)  # Store the product name at the time of purchase
    description = models.TextField(blank=True, null=True)  # Store a brief description
            
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity} x {self.name} in Order {self.order.order_number}"

    @property
    def total_price(self):
        if self.quantity is not None and self.price is not None:
            return self.quantity * self.price
        return None

    def save(self, *args, **kwargs):
        if self.product:
            # Update fields based on the current product state
            self.name = self.product.name
            self.description = self.product.description
            
            if self.price is None:
                self.price = self.product.price
        super().save(*args, **kwargs)

    # def apply_discount(self, amount=None, percentage=None):
    #     if amount:
    #         self.discount_amount = amount
    #     elif percentage:
    #         self.discount_percentage = percentage
    #     self.save()
