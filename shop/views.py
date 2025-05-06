from django.shortcuts import render
from .models import Banner, Category

def home_view(request):
    banners = Banner.objects.all()
    categories = Category.objects.filter(image__isnull=False)[:4]
    return render(request, 'shop/home.html', {'banners' : banners, 'categories': categories})


