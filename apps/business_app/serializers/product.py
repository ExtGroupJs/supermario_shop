from rest_framework import serializers

from apps.business_app.models.product import Product
from apps.business_app.serializers.model import ModelSerializer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "model")


class ReadProductSerializer(ProductSerializer):
    model = ModelSerializer()

    class Meta(ProductSerializer.Meta):
        model = Product
