from rest_framework import serializers

from apps.business_app.models.sell import Sell
from datetime import datetime

from apps.users_app.models.groups import Groups


class SellSerializer(serializers.ModelSerializer):
    shop_product = serializers.CharField(
        source="shop_product.__str__", read_only=True
    )
    unit_price = serializers.CharField(source="shop_product.sell_price", read_only=True)
    seller = serializers.CharField(source="seller.__str__", read_only=True)
    total_priced = serializers.SerializerMethodField()
    created_timestamp = serializers.SerializerMethodField()
    profits = serializers.SerializerMethodField()

    class Meta:
        model = Sell
        fields = (
            "id",
            "shop_product",
            "seller",
            "extra_info",
            "quantity",
            "unit_price",
            "total_priced",
            "created_timestamp",
            "profits",
        )
        read_only_fields = (
            "id",
            "__str__",
        )

    def get_created_timestamp(self, object):
        return object.created_timestamp.strftime("%d-%h-%Y a las  %I:%M %p")

    def get_total_priced(self, object):
        return object.quantity * object.shop_product.sell_price

    def get_profits(self, object):
        return (
            object.shop_product.sell_price - object.shop_product.cost_price
        ) * object.quantity

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (
            self.context.get("request")
            .user.groups.exclude(
                id__in=[Groups.SHOP_OWNER.value, Groups.SUPER_ADMIN.value]
            )
            .exists()
        ):
            response.pop("profits")
        return response
