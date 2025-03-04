from rest_framework import serializers

from apps.business_app.models.product import Product
from apps.business_app.serializers.model import (
    CatalogModelSerializer,
    ReadModelSerializer,
)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "model",
            "image",
        )


class ReadProductSerializer(ProductSerializer):
    model = ReadModelSerializer()
    model_name = serializers.CharField(read_only=True)

    class Meta(ProductSerializer.Meta):
        model = Product
        fields = ProductSerializer.Meta.fields + ("id", "model_name", "__str__")


class CatalogProductSerializer(ProductSerializer):
    model = CatalogModelSerializer()
    model_name = serializers.CharField(read_only=True)

    class Meta(ProductSerializer.Meta):
        model = Product
        fields = ("name", "model", "image", "model_name", "__str__")
