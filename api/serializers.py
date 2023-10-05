from rest_framework import serializers

from app.define import APP_VALUE_STATUS_CHOICES
from app.models import Product, CategoryChild, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class CategoryChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryChild
        fields = ("id", "name")


class ProductSerializer(serializers.ModelSerializer):
    category = CategoryChildSerializer()

    class Meta:
        model = Product
        exclude = ("status", "admin")
