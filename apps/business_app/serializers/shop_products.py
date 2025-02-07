from datetime import timedelta
import datetime
from rest_framework import serializers

from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.product import (
    CatalogProductSerializer,
    ReadProductSerializer,
)
from apps.users_app.models.groups import Groups


class ShopProductsSerializer(serializers.ModelSerializer):
    updated_timestamp = serializers.SerializerMethodField()

    shop_name = serializers.CharField(read_only=True)
    product_name = serializers.CharField(read_only=True)

    class Meta:
        model = ShopProducts
        fields = (
            "id",
            "quantity",
            "cost_price",
            "sell_price",
            "shop",
            "shop_name",
            "product",
            "product_name",
            "extra_info",
            "created_timestamp",
            "updated_timestamp",
            "__repr__",
        )

    def get_updated_timestamp(self, object):
        return object.updated_timestamp.strftime("%d-%h-%Y")
        # return object.updated_timestamp.strftime("%d-%h-%Y a las  %I:%M %p") # con hora


class ReadShopProductsSerializer(ShopProductsSerializer):
    product = ReadProductSerializer(read_only=True)
    product_name = serializers.CharField(read_only=True)

    class Meta(ShopProductsSerializer.Meta):
        model = ShopProducts
        fields = ShopProductsSerializer.Meta.fields

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (
            self.context.get("request")
            .user.groups.exclude(
                id__in=[Groups.SHOP_OWNER.value, Groups.SUPER_ADMIN.value]
            )
            .exists()
        ):
            response.pop("cost_price", None)
        return response


class CatalogShopProductSerializer(ReadShopProductsSerializer):
    one_month_ago = datetime.datetime.now() - timedelta(days=30)

    product = CatalogProductSerializer(read_only=True)

    class Meta(ReadShopProductsSerializer.Meta):
        fields = (
            "id",
            "sell_price",
            "product",
            "shop_name",
            "__repr__",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["is_new"] = instance.updated_timestamp >= self.one_month_ago
        return response
