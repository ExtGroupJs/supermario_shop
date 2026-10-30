from rest_framework import serializers

from apps.business_app.models.product import Product
from apps.business_app.serializers.model import (
    CatalogModelSerializer,
    ReadModelSerializer,
)


def _gallery_image_urls(obj):
    return [
        gallery.image.url
        for gallery in obj.gallery.all()
        if getattr(gallery, "image", None)
    ]


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
    shop_locations = serializers.SerializerMethodField(read_only=True)
    gallery = serializers.SerializerMethodField(read_only=True)

    class Meta(ProductSerializer.Meta):
        model = Product
        fields = ProductSerializer.Meta.fields + (
            "id",
            "model_name",
            "__str__",
            "shop_locations",
            "gallery",
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

    def get_gallery(self, obj):
        return _gallery_image_urls(obj)


class CatalogProductSerializer(ProductSerializer):
    model = CatalogModelSerializer()
    model_name = serializers.CharField(read_only=True)
    gallery = serializers.SerializerMethodField(read_only=True)

    class Meta(ProductSerializer.Meta):
        model = Product
        fields = ("name", "model", "image", "model_name", "__str__", "gallery")

    def get_gallery(self, obj):
        return _gallery_image_urls(obj)
