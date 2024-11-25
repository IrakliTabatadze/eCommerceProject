from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ManyToManyField(Category, related_name='products', blank=True)
    image = models.ImageField(upload_to='products', null=True, blank=True)

    def __str__(self):
        return self.name
