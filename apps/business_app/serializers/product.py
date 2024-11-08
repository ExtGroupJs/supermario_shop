from rest_framework import serializers

from apps.business_app.models.product import Product
from apps.business_app.serializers.model import ModelSerializer


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
    model_name = serializers.CharField(read_only = True)

    class Meta(ProductSerializer.Meta):
        model = Product
        fields = ProductSerializer.Meta.fields + ("id", "model_name", "__str__")
