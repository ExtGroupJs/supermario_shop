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
            "internal_code",
            "description",
            "model",
            "image",
        )


class ReadProductSerializer(ProductSerializer):
    model = ReadModelSerializer()
    model_name = serializers.CharField(read_only=True)
    shop_locations = serializers.SerializerMethodField(read_only=True)

    class Meta(ProductSerializer.Meta):
        model = Product
        fields = ProductSerializer.Meta.fields + (
            "id",
            "model_name",
            "__str__",
            "shop_locations",
        )

    def get_shop_locations(self, obj):
        locations = []
        shopproducts = obj.shopproducts_set.filter(
            deleted__isnull=True, shop__enabled=True
        ).select_related("shop").order_by("shop__name")
        for sp in shopproducts:
            locations.append(
                {
                    "shop_name": sp.shop.name,
                    "quantity": sp.quantity,
                }
            )
        return locations


class CatalogProductSerializer(ProductSerializer):
    model = CatalogModelSerializer()
    model_name = serializers.CharField(read_only=True)

    class Meta(ProductSerializer.Meta):
        model = Product
        fields = ("internal_code", "name", "model", "image", "model_name", "__str__")
