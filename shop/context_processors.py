from .models import Category
from .cart import Cart

def categories_context(request):
    return {
        'nav_categories': Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    }


def cart_context(request):
    return {
        'cart_item_count': len(Cart(request))
    }
