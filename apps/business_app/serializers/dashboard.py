from rest_framework import serializers

from apps.business_app.models.product import Product
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts


class DashboardSerializer(serializers.Serializer):
    updated_timestamp__gte = serializers.DateField(required=False)
    updated_timestamp__lte = serializers.DateField(required=False)


class DashboardSerializer(DashboardSerializer):
    frequency = serializers.ChoiceField(
        choices=["day", "week", "month", "quarter", "year"], required=False
    )
    shop_product__shop = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(), required=False
    )
    shop_product = serializers.PrimaryKeyRelatedField(
        queryset=ShopProducts.objects.all(), required=False
    )


class DashboardInvestmentSerializer(DashboardSerializer):
    shop = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(), required=False
    )
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=False
    )
