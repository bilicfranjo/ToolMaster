from .models import Category

def categories_context(request):
    return {
        'nav_categories': Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    }


def cart_context(request):
    if request.user.is_authenticated:
        cart = getattr(request.user, 'cart', None)
        if cart:
            count = sum(item.quantity for item in cart.items.all())
            return {'cart_item_count': count}
    return {'cart_item_count': 0}
