import json

from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Case, When, CharField, Value
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    JsonResponse,
    HttpResponseBadRequest,
)
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from app.forms import SignupForm, UpdateProfileForm
from app.models import *
from app.signals import user_created


# Create your views here.
class IndexView(generic.ListView):
    template_name = "app/index.html"
    context_object_name = "product_list"
    paginate_by = 3

    def get_queryset(self):
        if "category" in self.request.GET:
            return (
                Product.objects.select_related("category")
                .filter(category=self.request.GET["category"])
                .order_by("-pk")
            )

        if "category_child" in self.request.GET:
            return Product.objects.filter(
                category=self.request.GET["category_child"]
            ).order_by("-pk")

        return Product.objects.order_by("-pk")


class DetailView(generic.DetailView):
    model = Product
    template_name = "app/product.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product = self.get_object()
        context["product"] = product

        sizes = product.sizes.filter(product_size__quantity__gt=0).values(
            "id", "name", "product_size__quantity"
        )
        context["sizes"] = sizes

        return context


def signup(request):
    form = SignupForm()
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                new_user = form.save()
                user_created.send(sender=User, instance=new_user, created=True)
            return HttpResponseRedirect("/login")
    return render(request, "app/layout/signup.html", {"form": form})


def add_to_cart(request, product_id):
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("app:login"))

    product = Product.objects.get(id=product_id)
    size_id = request.POST["size"]
    size = Size.objects.get(id=size_id)
    try:
        cart_obj = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart_obj = Cart.objects.create(user=request.user)

    color = request.POST["color"]
    material = request.POST["material"]
    cart_item, created = Cart_item.objects.get_or_create(
        cart=cart_obj, product=product, size=size, color=color, material=material
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return HttpResponseRedirect(
        reverse(
            "app:cart",
        )
    )


def update_item_cart(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("app:login"))

    cart_id = request.GET.get("cart_id")
    product_id = request.GET.get("product_id")
    type_update = request.GET.get("type_update")
    size_id = request.GET.get("size")
    stock = Product_size.objects.get(product_id=product_id, size_id=size_id).quantity
    cart_item = Cart_item.objects.get(product_id=product_id, cart_id=cart_id)
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if is_ajax:
        if request.method == "GET":
            if type_update == "minus":
                if cart_item.quantity > 0:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
            elif type_update == "plus" and cart_item.quantity < stock:
                cart_item.quantity += 1
                cart_item.save()
            elif type_update == "remove":
                cart_item.delete()

            return JsonResponse({"Message": "Success"}, status=200)
        return JsonResponse({"status": "Invalid request"}, status=400)
    else:
        return HttpResponseBadRequest("Invalid request")


def cart(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("app:login"))
    try:
        cart_obj = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart_obj = Cart.objects.create(user=request.user)

    cart_items = Cart_item.objects.select_related("product", "size").filter(
        cart=cart_obj
    )

    context = {
        "cart_items": cart_items,
        "cart": cart_obj,
    }

    return render(
        request,
        "app/cart.html",
        context,
    )


def checkout(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("app:login"))

    cart_obj = Cart.objects.get(user=request.user)
    cart_items = Cart_item.objects.select_related("product", "size").filter(
        cart=cart_obj
    )
    context = {
        "cart": cart_obj,
        "cart_items": cart_items,
    }

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            name_receiver=request.POST["name_receiver"],
            phone_receiver=request.POST["phone_receiver"],
            address_receiver=request.POST["address_receiver"]
            + ", "
            + request.POST["address_last"],
            status=APP_VALUE_STATUS_DEFAULT,
            note=request.POST["note"],
            cart=cart_obj,
            total=cart_obj.get_total_price,
        )
        for item in cart_items:
            Order_product.objects.create(
                order=order,
                product=item.product,
                name=item.product.name,
                size=item.size,
                color=item.color,
                material=item.material,
                quantity=item.quantity,
                price=item.product.price,
            )
            item.delete()

        return HttpResponseRedirect(reverse("app:index"))
    return render(request, "app/checkout.html", context)


# data = list(cart_obj)
# json_data = json.dumps(data)
# return HttpResponse(json_data, content_type="application/json")


def search(request):
    if request.method == "GET":
        q = request.GET.get("term", "")
        product_list = Product.objects.filter(name__contains=q).values(
            "id", "name", "price", "image"
        )

        data = list(product_list)
        return JsonResponse(data, safe=False, status=200)
    return JsonResponse({"status": "Invalid request"}, status=400)


def profile(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("app:login"))

    user = request.user
    order_list = (
        Order.objects.annotate(
            status_label=Case(
                *[
                    When(status=code, then=Value(label))
                    for code, label in APP_VALUE_STATUS_ORDER_CHOICES
                ],
                default=Value("Unknown"),
                output_field=CharField(),
            )
        )
        .filter(user=user)
        .order_by("-pk")
    )
    context = {
        "user": user,
        "order_list": order_list,
    }
    return render(request, "app/profile.html", context)


def update_profile(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("app:login"))
    data = {
        "username": request.user.username,
        "email": request.user.email,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
    }
    form = UpdateProfileForm(data)

    context = {
        "form": form,
        "username": request.user.username,
        "email": request.user.email,
    }
    if request.method == "POST":
        form = UpdateProfileForm(request.POST)
        if form.is_valid():
            # save to database
            form.save()
            return HttpResponseRedirect("/profile")
    return render(request, "app/update_profile.html", context)


def order(request, pk=None):
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("app:login"))

    user = request.user
    if request.method == "POST" and request.is_ajax():
        order_id = request.POST["id"]
        status = request.POST["status"]
        order = Order.objects.get(id=order_id, user=user)
        order.status = status
        order.save()

        return JsonResponse({"Message": "Success"}, status=200)

    if request.method == "GET":
        order = Order.objects.annotate(
            status_label=Case(
                *[
                    When(status=code, then=Value(label))
                    for code, label in APP_VALUE_STATUS_ORDER_CHOICES
                ],
                default=Value("Unknown"),
                output_field=CharField(),
            )
        ).get(id=pk, user=user)
        order_product = Order_product.objects.filter(order=order).select_related(
            "product"
        )
        context = {
            "order": order,
            "order_product": order_product,
        }
        return render(request, "app/order_detail.html", context)
