from django.conf import settings
from django.conf.urls.static import static

from . import views
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views

app_name = "app"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="app/layout/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page=reverse_lazy("app:index")),
        name="logout",
    ),
    path("profile/", views.profile, name="profile"),
    path("update-profile/", views.update_profile, name="update_profile"),
    path("cart/", views.cart, name="cart"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path(
        "update-item-cart/",
        views.update_item_cart,
        name="update_item_cart",
    ),
    path("checkout/", views.checkout, name="checkout"),
    path("order/", views.order, name="update_status_order"),
    path("order/<int:pk>", views.order, name="order_detail"),
    path("search", views.search, name="search"),
    path("tinymce/", include("tinymce.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
