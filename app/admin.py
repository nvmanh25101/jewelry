from django.contrib import admin

from .define import *
from .models import (
    Category,
    CategoryChild,
    Product,
    Size,
    ProductSize,
    Order,
    OrderProduct,
)


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "status")
    list_filter = ("status",)
    search_fields = ("name", "slug")
    # prepopulated_fields = {"slug": ("name",)}

    class Media:
        css = ADMIN_SRC_CSS
        js = ADMIN_SRC_JS


class CategoryChildAdmin(admin.ModelAdmin):
    list_display = ("name", "category")


class ProductSizeInline(admin.StackedInline):
    model = ProductSize
    extra = 0
    can_delete = False


class ProductAdmin(admin.ModelAdmin):
    exclude = ("admin",)
    list_display = (
        "name",
        "color",
        "material",
        "display_image",
        "price",
        "status",
        "category",
    )
    inlines = [ProductSizeInline]

    class Media:
        css = ADMIN_SRC_CSS
        js = ADMIN_SRC_JS


class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "size", "quantity")

    class Media:
        css = ADMIN_SRC_CSS
        js = ADMIN_SRC_JS


class ProductInline(admin.StackedInline):
    model = OrderProduct
    extra = 0
    readonly_fields = (
        "name",
        "size",
        "color",
        "material",
        "quantity",
        "price",
    )
    can_delete = False
    max_num = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name_receiver", "status", "created_at")
    list_filter = ("status",)
    inlines = [ProductInline]
    readonly_fields = (
        "user",
        "name_receiver",
        "phone_receiver",
        "address_receiver",
        "total",
        "note",
        "created_at",
        "updated_at",
    )

    class Media:
        css = ADMIN_SRC_CSS
        js = ADMIN_SRC_JS

    def save_model(self, request, obj, form, change):
        if obj.id:
            original_order = Order.objects.get(id=obj.id)
            if original_order.admin is None:
                obj.admin = request.user

        super().save_model(request, obj, form, change)


class SizeAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(ProductSize, ProductSizeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CategoryChild, CategoryChildAdmin)
