from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True ,blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    featured = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True ,blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    popular = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    
    def __str__(self):
        return self.name

    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='extra_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Slika za {self.product.name}"


class ProductAttribute(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"

    
class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    
class Banner(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    

class DIYVideo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video = models.FileField(upload_to='diy_videos/')
    thumbnail = models.ImageField(upload_to='diy_thumbnails/', null=True, blank=True)
    video_thumbnail = models.ImageField(upload_to='diy_video_thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tools_used = models.ManyToManyField(Product, blank=True)
    
    def __str__(self):
        return self.title
    

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Na čekanju'),
        ('processing', 'U obradi'),
        ('shipped', 'Poslana'),
        ('completed', 'Dovršena'),
        ('cancelled', 'Otkazana'),
    ]

    code = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)


    def __str__(self):
        return f"{self.code} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.code:
            from uuid import uuid4
            self.code = f"ORD-{uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    def total(self):
        return self.price * self.quantity
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField("Broj mobitela", max_length=20, blank=True)
    address = models.TextField("Adresa", blank=True)

    def __str__(self):
        return f"Profil: {self.user.username}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Košarica ({self.user.username})"

    def total_price(self):
        return sum(item.total() for item in self.items.all()) # type: ignore 


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    def total(self):
        return self.product.price * self.quantity