from django.shortcuts import render
from .models import Banner

def home_view(request):
    banners = Banner.objects.all()
    return render(request, 'shop/home.html', {'banners' : banners,})


