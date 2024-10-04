from rest_framework import serializers

from apps.business_app.models.brand import Brand
from apps.business_app.models.sell import Sell


class SellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sell
        fields = (
            "id",
            "shop_product",
            "seller",
            "extra_info",
            "quantity",
        )
        read_only_fields = ("id", "__str__")
