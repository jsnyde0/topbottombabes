from django.shortcuts import render
from .models import Product
import logging

logger = logging.getLogger(__name__)

def view_list(request):
    # use custom 'filter_by_params' to filter the products on request.GET search parameters
    products = Product.objects.filter_by_params(**request.GET)
    
    return render(request, 'products/product_list.html', {'products': products})