from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.html import format_html

from .define import *
from .helpers import *


# Create your models here.
class Category(models.Model):
    name = models.CharField(unique=True, max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    status = models.IntegerField(
        choices=APP_VALUE_STATUS_CHOICES,
        default=APP_VALUE_STATUS_DEFAULT,
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class CategoryChild(models.Model):
    name = models.CharField(unique=True, max_length=200)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="category_children"
    )

    class Meta:
        verbose_name_plural = "Category child"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(unique=True, max_length=200)
    color = models.CharField(max_length=200)
    material = models.CharField(max_length=200)
    image = models.ImageField(upload_to=get_file_path, null=True)
    price = models.IntegerField()
    description = models.TextField()
    status = models.IntegerField(
        choices=APP_VALUE_STATUS_CHOICES,
        default=APP_VALUE_STATUS_DEFAULT,
    )
    category = models.ForeignKey(CategoryChild, on_delete=models.CASCADE)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return self.name

    @cached_property
    def display_image(self):
        html = '<img src="{img}" class="admin-image">'
        if self.image:
            return format_html(html, img=self.image.url)
        return format_html("<strong>There is no image for this entry.<strong>")


class Size(models.Model):
    name = models.CharField(unique=True, max_length=200)
    products = models.ManyToManyField(
        Product, through="ProductSize", related_name="sizes"
    )

    def __str__(self):
        return self.name


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return str(self.id)


class Order(models.Model):
    name_receiver = models.CharField(max_length=200)
    phone_receiver = models.CharField(max_length=200)
    address_receiver = models.CharField(max_length=200)
    status = models.IntegerField(
        choices=APP_VALUE_STATUS_ORDER_CHOICES,
        default=APP_VALUE_STATUS_DEFAULT,
    )
    total = models.IntegerField()
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="user"
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="admin",
        null=True,
        editable=False,
    )
    cart = models.ForeignKey(
        "Cart", on_delete=models.PROTECT, null=True, editable=False
    )

    def __str__(self):
        return str(self.id)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, editable=False)
    name = models.CharField(max_length=200)
    size = models.CharField(max_length=15)
    color = models.CharField(max_length=50)
    material = models.CharField(max_length=50)
    quantity = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return str(self.name)

    @property
    def get_total_price(self):
        total = self.product.price * self.quantity
        return total


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_total_item(self):
        total = len(self.cartitem_set.all())
        return total

    @property
    def get_total_price(self):
        total = 0
        for item in self.cartitem_set.all():
            total += item.get_total_price
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    color = models.CharField(max_length=50)
    material = models.CharField(max_length=50)

    @property
    def get_total_price(self):
        total = self.product.price * self.quantity
        return total
