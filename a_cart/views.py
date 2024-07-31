from django.shortcuts import render
from .models import Cart
from a_products.models import Product
from django.contrib.auth.decorators import login_required

def view_cart(request):
    cart, created = Cart.get_or_create_from_request(request)
    return render(request, 'cart/cart.html', {'cart': cart})

def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        if product_id:
            cart, created = Cart.get_or_create_from_request(request)
            product = Product.objects.get(id=product_id)
            cart.add_product(product, quantity)
            if request.htmx:
                return render(request, 'cart/cart_content.html', {'cart': cart})
            return render(request, 'cart/cart.html', {'cart': cart})
    return render(request, 'cart/cart.html', {'error': 'Invalid product or quantity'})

def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart, created = Cart.get_or_create_from_request(request)
        cart.remove_product(product_id)
        if request.htmx:
            return render(request, 'cart/cart_content.html', {'cart': cart})
        return render(request, 'cart/cart.html', {'cart': cart})
    return render(request, 'cart/cart.html', {'error': 'Invalid product'})

def update_quantity(request):
    cart, created = Cart.get_or_create_from_request(request)
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    cart.update_quantity(product_id, quantity)
    if request.htmx:
        return render(request, 'cart/cart_content.html', {'cart': cart})
    return render(request, 'cart/cart.html', {'cart': cart})