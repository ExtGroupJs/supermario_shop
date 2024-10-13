from rest_framework import serializers

from apps.business_app.models.sell import Sell
from datetime import datetime


class SellSerializer(serializers.ModelSerializer):
    shop_product_name = serializers.CharField(
        source="shop_product.__str__", read_only=True
    )
    unit_price = serializers.CharField(source="shop_product.sell_price", read_only=True)
    seller_name = serializers.CharField(source="seller.__str__", read_only=True)
    total_priced = serializers.SerializerMethodField(read_only=True)
    created_timestamp = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Sell
        fields = (
            "id",
            "shop_product",
            "shop_product_name",
            "seller_name",
            "extra_info",
            "quantity",
            "unit_price",
            "total_priced",
            "created_timestamp",
        )
        read_only_fields = (
            "id",
            "__str__",
        )

    def get_created_timestamp(self, object):
        return object.created_timestamp.strftime("%d-%h-%Y a las  %I:%M %p")

    def get_total_priced(self, object):
        return object.quantity * object.shop_product.sell_price
