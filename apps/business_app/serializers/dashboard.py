from rest_framework import serializers

from apps.business_app.models.product import Product
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts
from apps.common.utils.allowed_frequencies import AllowedFrequencies


class DashboardSerializer(serializers.Serializer):
    updated_timestamp__gte = serializers.DateField(required=False)
    updated_timestamp__lte = serializers.DateField(required=False)


class DashboardCountsSerializer(DashboardSerializer):
    frequency = serializers.ChoiceField(
        choices=AllowedFrequencies.choices, required=False
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
