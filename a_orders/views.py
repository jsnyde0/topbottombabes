from django.shortcuts import render, redirect
from .models import Order
from a_cart.models import Cart
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def checkout(request):
    cart, created = Cart.get_or_create_cart(request)
    if created:
        logger.info(f"Tried checking out without a Cart; redirecting to cart for user {request.user}")
        return redirect('cart:view_cart')
    
    # get or create an order and sync it with the cart
    order = Order.create_order_from_request(request, sync_with_cart=True)
    context = {'order': order}
    return render(request, 'orders/checkout.html', context)