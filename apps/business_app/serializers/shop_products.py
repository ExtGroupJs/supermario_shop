from rest_framework import serializers

from apps.business_app.models.shop_products import ShopProducts


class ShopProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopProducts
        fields = "__all__"
