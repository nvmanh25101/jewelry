from rest_framework import routers
from django.urls import path, include
from . import views

app_name = "api"
urlpatterns = [
    path(
        "categories/", views.CategoryListAPIView.as_view(), name="CategoryListAPIView"
    ),
    path(
        "categories/<int:pk>/",
        views.CategoryDetailAPIView.as_view(),
        name="CategoryDetailAPIView",
    ),
    path("products/", views.ProductAPIView.as_view(), name="ProductAPIView"),
]
