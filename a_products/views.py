from django.shortcuts import render
from .models import Product

def home(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})