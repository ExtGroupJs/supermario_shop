from email.policy import default
from rest_framework import serializers

from apps.business_app.models.sell import Sell
from datetime import datetime

from apps.business_app.serializers.sell_group import SellGroupSerializer


class SellSerializer(serializers.ModelSerializer):
    shop_product__product__name = serializers.CharField(
        source="shop_product.__str__", read_only=True
    )
    shop_product__sell_price = serializers.CharField(
        source="shop_product.sell_price", read_only=True
    )
    seller__first_name = serializers.CharField(source="seller.__str__", read_only=True)
    total_priced = serializers.FloatField(read_only=True)
    created_timestamp = serializers.SerializerMethodField()
    profits = serializers.FloatField(read_only=True)
    sell_group = SellGroupSerializer(read_only=True)

    class Meta:
        model = Sell
        fields = (
            "id",
            "shop_product",
            "shop_product__product__name",
            "seller__first_name",
            "extra_info",
            "quantity",
            "shop_product__sell_price",
            "total_priced",
            "created_timestamp",
            "profits",
            "sell_group",
        )
        read_only_fields = (
            "id",
            "__str__",
        )

    def get_created_timestamp(self, object):
        return object.created_timestamp.strftime("%d-%h-%Y a las  %I:%M %p")
