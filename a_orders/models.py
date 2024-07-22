from django.db import models
from django.db.models import Sum, F
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from a_products.models import Product

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
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
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

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    @property
    def compute_total_price(self):
        total = self.items.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0
        return total

    def save(self, *args, **kwargs):
        # precompute the total price
        if not self.total_price:
            self.total_price = self.compute_total_price
        # set the order number by getting previous one and incrementing by 1
        if not self.order_number:
            last_order = Order.objects.all().order_by('id').last()
            if not last_order:
                self.order_number = '000001'
            else:
                last_order_number = int(last_order.order_number)
                new_order_number = last_order_number + 1
                self.order_number = f'{new_order_number:06d}'
        super().save(*args, **kwargs)



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
