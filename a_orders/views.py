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
        return redirect('a_cart:view_cart')
    
    order = Order.create_from_cart(cart)
    context = {'order': order}
    return render(request, 'orders/checkout.html', context)