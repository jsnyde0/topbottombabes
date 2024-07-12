from django.shortcuts import render
from .models import Product, Category, Purpose, Material, BodyPart
import logging

logger = logging.getLogger(__name__)

def view_list(request):
    # use custom 'filter_by_params' to filter the products on request.GET search parameters
    products = Product.objects.filter_by_params(**request.GET)
    print('Products count: ', products.count())

    context = {
        'products': products,
        'categories': Category.objects.all(),
        'purposes': Purpose.objects.all(),
        'materials': Material.objects.all(),
        'body_parts': BodyPart.objects.all(),
    }
    
    # if request.htmx:
    #     return render(request, 'products/product_list.html#product_list', context)
    return render(request, 'products/product_list.html', context)