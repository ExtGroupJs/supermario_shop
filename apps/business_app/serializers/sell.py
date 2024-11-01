from rest_framework import serializers

from apps.business_app.models.sell import Sell
from datetime import datetime

from apps.users_app.models.groups import Groups


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
        )
        read_only_fields = (
            "id",
            "__str__",
        )

    def get_created_timestamp(self, object):
        return object.created_timestamp.strftime("%d-%h-%Y a las  %I:%M %p")


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
