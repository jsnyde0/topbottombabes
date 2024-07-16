from django.shortcuts import render
from .models import Product, Category, Purpose, Material, BodyPart
from a_cart.models import Cart
import logging
import time

logger = logging.getLogger(__name__)

def view_list(request):
    # use custom 'filter_by_params' to filter the products on request.GET search parameters
    products = Product.objects.filter_by_params(**request.GET)
    cart, created = Cart.objects.get_or_create(user=request.user)  

    context = {'products': products, 'cart': cart}
    
    time.sleep(1)

    if request.htmx:
        return render(request, 'cotton/product_list.html', context)
    
    # if it's not an HTMX request, we also have to get the categories, materials etc to render the whole page
    context.update({
            'categories': Category.objects.all(),
            'purposes': Purpose.objects.all(),
            'materials': Material.objects.all(),
            'body_parts': BodyPart.objects.all(),
        })
    return render(request, 'products/product_list.html', context)

def view_product(request, slug):
    product = Product.objects.get(slug=slug)
    context = {'product': product}

    if request.htmx:
        return render(request, 'products/product_detail_content.html', context)    
    return render(request, 'products/product_detail.html', context)