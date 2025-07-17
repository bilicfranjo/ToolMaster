from django.contrib import admin
from .models import (
    Category, Product, Banner, DIYVideo,
    ProductImage, ProductAttribute, ProductAttributeValue,
    Order, OrderItem, UserProfile, Cart, CartItem)


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Banner)
admin.site.register(DIYVideo)
admin.site.register(ProductImage)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(UserProfile)
admin.site.register(Cart)
admin.site.register(CartItem)

