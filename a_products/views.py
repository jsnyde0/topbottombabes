from django.shortcuts import render
from .models import Product, Category, Purpose, Material, BodyPart
import logging
import time

logger = logging.getLogger(__name__)

def view_list(request):
    # use custom 'filter_by_params' to filter the products on request.GET search parameters
    products = Product.objects.filter_by_params(**request.GET)
    print('Products count: ', products.count())

    context = {'products': products}
    
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