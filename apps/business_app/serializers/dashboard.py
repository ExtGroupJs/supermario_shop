from rest_framework import serializers

from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts
from apps.common.utils.allowed_frequencies import AllowedFrequencies


class DashboardSerializer(serializers.Serializer):
    updated_timestamp__gte = serializers.DateField(required=False)
    updated_timestamp__lte = serializers.DateField(required=False)


class DashboardSellGroupSerializer(serializers.Serializer):
    """Filters of the dashboard tiles, resolved on the sell group.

    The dashboard measures sales by sell group, so the period is the moment the group
    was registered (``created_timestamp``) and not the moment each one of its sells was
    touched: a group is never cut in half by its own lines. It does not inherit
    ``DashboardSerializer`` on purpose, that one filters ``updated_timestamp`` of a sell,
    which is not a field of this payload anymore.
    """

    created_timestamp__gte = serializers.DateField(required=False)
    created_timestamp__lte = serializers.DateField(required=False)
    frequency = serializers.ChoiceField(
        choices=AllowedFrequencies.choices, required=False
    )
    # A sell group has no shop of its own, it belongs to the shop of its products, so
    # the view resolves this instead of letting the serializer filter a missing field.
    shop_id = serializers.PrimaryKeyRelatedField(
        source="shop", queryset=Shop.objects.all(), required=False
    )
    shop = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(), required=False
    )


class DashboardCountsSerializer(DashboardSerializer):
    frequency = serializers.ChoiceField(
        choices=AllowedFrequencies.choices, required=False
    )
    shop_id = serializers.PrimaryKeyRelatedField(
        source="shop_product__shop", queryset=Shop.objects.all(), required=False
    )
    shop_product__shop = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(), required=False
    )
    shop_product = serializers.PrimaryKeyRelatedField(
        queryset=ShopProducts.objects.all(), required=False
    )
