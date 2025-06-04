from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Banner, Category, Product, DIYVideo, ProductAttribute, ProductAttributeValue, Order, UserProfile, OrderItem
from django.contrib.auth import login, authenticate, logout
from .forms import CustomAuthenticationForm, CustomUserCreationForm, ProductForm, DIYVideoForm, BannerForm, CategoryForm, ProductAttributeFormSet, ProductImageFormSet, ProfileUpdateForm, CheckoutForm
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

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


# Proizvodi
def products_list_view(request, slug=None):
    products = Product.objects.all()
    category = None
    manufacturers = Product.objects.values_list('manufacturer', flat=True).distinct().exclude(manufacturer='')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    attribute_filters = []
    attribute_queries = Q()

    if slug:
        category = get_object_or_404(Category, slug=slug)
        if category.subcategories.exists(): # type: ignore
            subcategories = category.subcategories.all() # type: ignore
            products = products.filter(category__in=subcategories)
        else:
            products = products.filter(category=category)
            attribute_filters = ProductAttribute.objects.filter(category=category)

    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            pass

    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass

    # Višestruki proizvođači (checkbox logika)
    selected_manufacturers = request.GET.getlist('manufacturer')
    if selected_manufacturers:
        products = products.filter(manufacturer__in=selected_manufacturers)

    # Višestruki atributi (checkbox logika po OR-u)
    selected_attributes = {}
    attribute_queries = Q()

    for key, values in request.GET.lists():
        if key.startswith('attr_'):
            selected_attributes[key] = values
            attr_id = key.split('_')[1]
            subquery = Q()

            for val in values:
                subquery |= Q(attributes__attribute_id=attr_id, attributes__value=val)

            attribute_queries |= subquery  # Ovdje je ključna razlika: koristimo OR između atributa

    if attribute_queries:
        products = products.filter(attribute_queries).distinct()


    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'manufacturer_asc':
        products = products.order_by('manufacturer')
    elif sort_by == 'manufacturer_desc':
        products = products.order_by('-manufacturer')

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/products_list.html', {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'category': category,
        'selected_manufacturers': selected_manufacturers,
        'sort_by': sort_by,
        'paginator': paginator,
        'categories': Category.objects.filter(parent__isnull=True).prefetch_related('subcategories'),
        'manufacturers': manufacturers,
        'price_min': price_min,
        'price_max': price_max,
        'attribute_filters': attribute_filters,
        'selected_attributes': selected_attributes,
    })


def product_detail_view(request, category_slug ,slug):
    product = get_object_or_404(Product, slug=slug, category__slug=category_slug)
    product_attributes = product.attributes.select_related('attribute') # type: ignore
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'product_attributes': product_attributes,
    })
    

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
                next_url = request.GET.get('next') or request.POST.get('next')
                return redirect(next_url) if next_url else redirect('home')

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

"""
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
"""

@staff_member_required
def admin_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            # Atributi
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
        formset = ProductImageFormSet()
    return render(request, 'shop/dashboard/product_form_dashboard.html', {
        'form': form,
        'formset': formset,
        'action': 'Dodaj novi proizvod',
        'attribute_values': {},
    })


"""
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
"""

@staff_member_required
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.save()
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
        formset = ProductImageFormSet(instance=product)
        attribute_values = {av.attribute.id: av.value for av in product.attributes.all()} # type: ignore
        return render(request, 'shop/dashboard/product_form_dashboard.html', {
            'form': form,
            'formset': formset,
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



# Košarica
@login_required
def cart_detail_view(request):
    cart = request.user.cart
    items = cart.items.select_related('product')
    subtotal = cart.total_price()
    shipping = 0 if subtotal >= 100 else 10.99
    total = subtotal + shipping

    return render(request, 'shop/cart.html', {
        'cart': cart,
        'items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    })

@login_required
def cart_add_view(request, product_id):
    cart = request.user.cart
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    item, created = cart.items.get_or_create(product=product)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()

    return JsonResponse({
    'cart_item_count': sum(i.quantity for i in cart.items.all())
    })


@login_required
def cart_remove_view(request, product_id):
    cart = request.user.cart
    cart.items.filter(product_id=product_id).delete()
    return redirect('cart_detail')

@login_required
def cart_update_view(request, product_id):
    cart = request.user.cart
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    item, created = cart.items.get_or_create(product=product)
    item.quantity = quantity
    item.save()

    return redirect('cart_detail')


# Naplata
@login_required
def checkout_view(request):
    cart = request.user.cart
    items = cart.items.select_related('product')
    user_profile = getattr(request.user, 'userprofile', None)

    if not items.exists():
        return redirect('cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Logika za adresu
            if form.cleaned_data['use_profile_address']:
                address = user_profile.address if user_profile and user_profile.address else ''
            else:
                address = form.cleaned_data['shipping_address']

            # Logika za telefon
            if form.cleaned_data['use_profile_phone']:
                phone = user_profile.phone if user_profile and user_profile.phone else ''
            else:
                phone = form.cleaned_data['phone']

            if not address or not phone:
                form.add_error(None, "Adresa i broj mobitela su obavezni.")
            else:
                order = Order.objects.create(
                    user=request.user,
                    total_price=cart.total_price(),
                    shipping_address=address,
                    phone=phone,
                )

                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price,
                    )

                items.delete()
                return redirect('order_success', pk=order.pk)
    else:
        form = CheckoutForm()

    return render(request, 'shop/checkout.html', {
        'form': form,
        'user_profile': user_profile,
    })


@login_required
def order_success_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'shop/order_success.html', {'order': order})
