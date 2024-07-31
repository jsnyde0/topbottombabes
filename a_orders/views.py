from django.shortcuts import render, redirect
from .models import Order
from a_cart.models import Cart
from .forms import ContactForm, ShippingForm
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def checkout_contact(request):
    cart, created = Cart.get_or_create_from_request(request)
    if created:
        logger.info(f"Tried checking out without a Cart; redirecting to cart for user {request.user}")
        return redirect('cart:view_cart')
    
    # get or create an order and sync it with the cart
    order, _ = Order.get_or_create_from_request(request, sync_with_cart=True)
    form = ContactForm()
    context = {'order': order, 'form': form}
    return render(request, 'orders/checkout_contact.html', context)

def checkout_shipping(request):
    # get the order
    order, created = Order.get_or_create_from_request(request, sync_with_cart=False)
    if created:
        logger.warning(f"Created a new order in checkout shipping step; this shouldn't happen!")

    form = ShippingForm()
    context = {'order': order, 'form': form}
    return render(request, 'orders/checkout_shipping.html', context)