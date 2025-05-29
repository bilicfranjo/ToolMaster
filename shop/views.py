from django.shortcuts import render, redirect
from .models import Banner, Category, Product, DIYVideo, ProductAttribute, ProductAttributeValue, Order
from django.contrib.auth import login, authenticate, logout
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ProductForm, DIYVideoForm, BannerForm, CategoryForm, ProductAttributeFormSet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Order, UserProfile
from .forms import ProfileUpdateForm

# Home 
def home_view(request):
    banners = Banner.objects.all()
    categories = Category.objects.filter(featured=True)
    popular_products = Product.objects.filter(popular=True)
    return render(request, 'shop/home.html', {
        'banners': banners,
        'categories': categories, 
        'popular_products' : popular_products,
        })

# Profil 
@login_required
def profile_view(request):
    profile = UserProfile.objects.get(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/profile.html', {
        'user': request.user,
        'profile': profile,
        'orders': orders,
    })


@login_required
def profile_edit_view(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user, profile=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = ProfileUpdateForm(instance=request.user, profile=profile)

    return render(request, 'shop/profile_edit.html', {'form': form})

@login_required
def user_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'shop/order_detail_user.html', {'order': order})


# Autentikacija
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

# DIY dio
def diy_list_view(request):
    videos = DIYVideo.objects.all().order_by("-created_at")
    return render(request, 'shop/diy_list.html', {'videos': videos})

def diy_detail_view(request, pk):
    video = DIYVideo.objects.get(pk=pk)
    return render(request, 'shop/diy_detail.html', {'video': video})

# Admin
@staff_member_required
def dashboard_home(request):
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:3]
    
    context = {
        'product_count': Product.objects.count(),
        'category_count': Category.objects.count(),
        'diy_count': DIYVideo.objects.count(),
        'user_count': User.objects.count(),
        'order_count': Order.objects.count(),
        'recent_orders': recent_orders,
    }
    return render(request, 'shop/dashboard/home_dashboard.html', context)

# Proizvodi admin
@staff_member_required
def admin_products_list(request):
    products = Product.objects.all().select_related('category')
    return render(request, 'shop/dashboard/products_list_dashboard.html', {'products': products})

@staff_member_required
def admin_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            # Spremi atribute
            for key, value in request.POST.items():
                if key.startswith('attribute_') and value.strip():
                    attr_id = key.split('_')[1]
                    ProductAttributeValue.objects.create(
                        product=product,
                        attribute_id=attr_id,
                        value=value.strip()
                    )
            return redirect('admin_products_list')
    else:
        form = ProductForm()
    return render(request, 'shop/dashboard/product_form_dashboard.html', {'form': form, 'action': 'Dodaj novi proizvod', 'attribute_values': {},})


@staff_member_required
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            product.attributes.all().delete()
            for key, value in request.POST.items():
                if key.startswith('attribute_') and value.strip():
                    attr_id = key.split('_')[1]
                    ProductAttributeValue.objects.create(
                        product=product,
                        attribute_id=attr_id,
                        value=value.strip()
                    )
            return redirect('admin_products_list')
    else:
        form = ProductForm(instance=product)
        attribute_values = {av.attribute.id: av.value for av in product.attributes.all()} # type: ignore
        return render(request, 'shop/dashboard/product_form_dashboard.html', {
            'form': form,
            'action': 'Uredi proizvod',
            'attribute_values': attribute_values,
        })



@staff_member_required
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
    return redirect('admin_products_list')


@staff_member_required
def get_attributes_for_category(request, category_id):
    attributes = ProductAttribute.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(attributes), safe=False)


# DIY admin
@staff_member_required
def admin_diy_list(request):
    videos = DIYVideo.objects.all().order_by('-created_at')
    return render(request, 'shop/dashboard/diy_list_dashboard.html', {'videos': videos})


@staff_member_required
def admin_diy_create(request):
    if request.method == 'POST':
        form = DIYVideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_diy_list')
    else:
        form = DIYVideoForm()
    return render(request, 'shop/dashboard/diy_form_dashboard.html', {'form': form, 'action': 'Dodaj DIY video'})


@staff_member_required
def admin_diy_edit(request, pk):
    video = get_object_or_404(DIYVideo, pk=pk)
    if request.method == 'POST':
        form = DIYVideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            return redirect('admin_diy_list')
    else:
        form = DIYVideoForm(instance=video)
    return render(request, 'shop/dashboard/diy_form_dashboard.html', {'form': form, 'action': 'Uredi DIY video'})


@staff_member_required
def admin_diy_delete(request, pk):
    video = get_object_or_404(DIYVideo, pk=pk)
    if request.method == 'POST':
        video.delete()
    return redirect('admin_diy_list')


# Banner admin
@staff_member_required
def admin_banner_list(request):
    banners = Banner.objects.all()
    return render(request, 'shop/dashboard/banners_list_dashboard.html', {'banners': banners})

@staff_member_required
def admin_banner_create(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_banner_list')
    else:
        form = BannerForm()
    return render(request, 'shop/dashboard/banner_form_dashboard.html', {'form': form, 'action': 'Dodaj banner'})

@staff_member_required
def admin_banner_edit(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            return redirect('admin_banner_list')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'shop/dashboard/banner_form_dashboard.html', {'form': form, 'action': 'Uredi banner'})

@staff_member_required
def admin_banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        banner.delete()
    return redirect('admin_banner_list')


# Kategorije admin
@staff_member_required
def admin_category_list(request):
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    return render(request, 'shop/dashboard/categories_list_dashboard.html', {'categories': categories})

@staff_member_required
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        formset = ProductAttributeFormSet(request.POST, queryset=ProductAttribute.objects.none())
        if form.is_valid() and formset.is_valid():
            category = form.save()
            for subform in formset:
                if subform.cleaned_data and not subform.cleaned_data.get('DELETE', False):
                    ProductAttribute.objects.create(
                        name=subform.cleaned_data['name'],
                        category=category
                    )
            return redirect('admin_category_list')
    else:
        form = CategoryForm()
        formset = ProductAttributeFormSet(queryset=ProductAttribute.objects.none())

    return render(request, 'shop/dashboard/category_form_dashboard.html', {
        'form': form,
        'formset': formset,
        'action': 'Dodaj kategoriju'
    })

@staff_member_required
def admin_category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        formset = ProductAttributeFormSet(request.POST, queryset=ProductAttribute.objects.filter(category=category))
        if form.is_valid() and formset.is_valid():
            form.save()
            for subform in formset:
                if subform.cleaned_data:
                    if subform.cleaned_data.get('DELETE'):
                        if subform.instance.pk:
                            subform.instance.delete()
                    else:
                        attr = subform.save(commit=False)
                        attr.category = category
                        attr.save()
            return redirect('admin_category_list')
    else:
        form = CategoryForm(instance=category)
        formset = ProductAttributeFormSet(queryset=ProductAttribute.objects.filter(category=category))

    return render(request, 'shop/dashboard/category_form_dashboard.html', {
        'form': form,
        'formset': formset,
        'action': 'Uredi kategoriju'
    })

@staff_member_required
def admin_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
    return redirect('admin_category_list')



# Korisnici admin
@staff_member_required
def admin_user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'shop/dashboard/users_list_dashboard.html', {'users': users})


@staff_member_required
def admin_user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST' and not user.is_superuser:
        user.delete()
    return redirect('admin_users_list')

@staff_member_required
def toggle_user_staff_status(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser:
        return redirect('admin_user_list')

    user.is_staff = not user.is_staff
    user.save()
    return redirect('admin_user_list')

# Narudžba admin
@staff_member_required
def admin_order_list(request):
    from .models import Order
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'shop/dashboard/orders_list_dashboard.html', {'orders': orders})


@staff_member_required
def admin_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return redirect('admin_order_detail', pk=pk)

    return render(request, 'shop/dashboard/order_detail_dashboard.html', {'order': order})
