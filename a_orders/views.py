from django.shortcuts import render, redirect
from .models import Order, Address
from a_cart.models import Cart
from .forms import ContactForm, AddressForm, PaymentForm
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
    form = ContactForm(request.POST or None, instance=order)
    if form.is_valid():
        form.save()
        return redirect('orders:checkout_shipping')
    context = {'order': order, 'form': form}
    return render(request, 'orders/checkout_contact.html', context)

def checkout_shipping(request):
    # get the order
    order, created = Order.get_or_create_from_request(request, sync_with_cart=False)
    if created:
        logger.warning(f"Created a new order in checkout shipping step; this shouldn't happen!")

    form = AddressForm(request.POST or None, instance=order.shipping_address)
    if form.is_valid():
        shipping_address = form.save(commit=False)
        shipping_address.type = 'Shipping'

        if request.user.is_authenticated:
            shipping_address.user = request.user

        shipping_address.save()

        order.shipping_address = shipping_address
        order.save()

        return redirect('orders:checkout_payment')
    
    context = {'order': order, 'form': form}
    return render(request, 'orders/checkout_shipping.html', context)

def checkout_payment(request):
    order, created = Order.get_or_create_from_request(request, sync_with_cart=False)
    if created:
        logger.warning(f"Created a new order in checkout payment step; this shouldn't happen!")

    form = PaymentForm(request.POST or None, instance=order)
    context = {'order': order, 'form': form}
    return render(request, 'orders/checkout_payment.html', context)