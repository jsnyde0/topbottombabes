from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem, Order

@receiver([post_save, post_delete], sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    """
    Signal to update Order total_price when OrderItems are added, modified, or deleted.
    """
    order = instance.order
    order.compute_total_price()
    order.save()