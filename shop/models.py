from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)
    in_stock = models.BooleanField(default=True)
    popular = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    
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
    


    