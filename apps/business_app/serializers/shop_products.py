from rest_framework import serializers

from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.product import (
    ProductSerializer,
    ReadProductSerializer,
)
from apps.business_app.serializers.shop import ShopSerializer
from apps.users_app.models.groups import Groups


class ShopProductsSerializer(serializers.ModelSerializer):
    created_timestamp = serializers.SerializerMethodField()
    class Meta:
        model = ShopProducts
        fields = (
            "id",
            "quantity",
            "cost_price",
            "sell_price",
            "shop",
            "product",
            "extra_info",
            "created_timestamp",
            "__repr__",
        )
    def get_created_timestamp(self, object):
        return object.created_timestamp.strftime("%d-%h-%Y a las  %I:%M %p")


class ReadShopProductsSerializer(ShopProductsSerializer):
    shop = ShopSerializer()
    product = ReadProductSerializer()

    class Meta(ShopProductsSerializer.Meta):
        model = ShopProducts

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (
            self.context.get("request")
            .user.groups.exclude(
                id__in=[Groups.SHOP_OWNER.value, Groups.SUPER_ADMIN.value]
            )
            .exists()
        ):
            response.pop("cost_price")
        return response
