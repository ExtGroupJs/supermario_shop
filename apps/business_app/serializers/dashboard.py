from rest_framework import serializers

from apps.business_app.models.product import Product
from apps.business_app.models.shop import Shop


class DashboardSerializer(serializers.Serializer):
    frequency = serializers.ChoiceField(choices=['day', 'week', 'month', 'quarter'], required=False)


class DashboardInvestmentSerializer(serializers.Serializer):
    updated_timestamp__gte = serializers.DateField(required=False)
    updated_timestamp__lte = serializers.DateField(required=False)
    shop = serializers.PrimaryKeyRelatedField(queryset = Shop.objects.all(), required=False)
    product = serializers.PrimaryKeyRelatedField(queryset = Product.objects.all(), required=False)

