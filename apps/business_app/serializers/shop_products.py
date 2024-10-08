from rest_framework import serializers

from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.product import (
    ProductSerializer,
    ReadProductSerializer,
)
from apps.business_app.serializers.shop import ShopSerializer


class ShopProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopProducts
        fields = "__all__"


class ReadShopProductsSerializer(ShopProductsSerializer):
    shop = ShopSerializer()
    product = ReadProductSerializer()

    class Meta(ShopProductsSerializer.Meta):
        model = ShopProducts
