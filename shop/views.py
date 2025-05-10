from django.shortcuts import render
from .models import Banner, Category, Product

def home_view(request):
    banners = Banner.objects.all()
    categories = Category.objects.filter(image__isnull=False)[:4]
    popular_products = Product.objects.filter(popular=True)
    return render(request, 'shop/home.html', {
        'banners': banners,
        'categories': categories, 
        'popular_products' : popular_products,
        })


