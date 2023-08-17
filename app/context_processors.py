from app.models import Category, Category_child, Cart


def shared_data(request):
    cart = ""
    category_list = Category.objects.prefetch_related("category_children").all()
    # category_list = Category.objects.order_by("-pk")
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        if cart:
            cart = cart[0]
    return {"category_list": category_list, "cart": cart}
