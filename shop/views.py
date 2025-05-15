from django.shortcuts import render, redirect
from .models import Banner, Category, Product, DIYVideo
from django.contrib.auth import login, authenticate, logout
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.contrib.auth.models import User

def home_view(request):
    banners = Banner.objects.all()
    categories = Category.objects.filter(image__isnull=False)[:4]
    popular_products = Product.objects.filter(popular=True)
    return render(request, 'shop/home.html', {
        'banners': banners,
        'categories': categories, 
        'popular_products' : popular_products,
        })


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    error_message = None

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                error_message = "Neispravno korisničko ime ili lozinka."
        else:
            error_message = "Neispravan unos. Pokušaj ponovno."
    else:
        form = CustomAuthenticationForm()

    return render(request, 'shop/login.html', {'form': form, 'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('home')

def diy_list_view(request):
    videos = DIYVideo.objects.all().order_by("-created_at")
    return render(request, 'shop/diy_list.html', {'videos': videos})


def diy_detail_view(request, pk):
    video = DIYVideo.objects.get(pk=pk)
    return render(request, 'shop/diy_detail.html', {'video': video})