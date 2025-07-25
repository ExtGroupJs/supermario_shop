from rest_framework import serializers

from apps.business_app.models.sell import Sell


class SellSerializer(serializers.ModelSerializer):
    sell_price = serializers.CharField(read_only=True)
    product_name = serializers.CharField(read_only=True)
    seller__first_name = serializers.CharField(source="seller.__str__", read_only=True)
    total_priced = serializers.FloatField(read_only=True)
    created_timestamp = serializers.SerializerMethodField()
    profits = serializers.FloatField(read_only=True)
    discounts = serializers.FloatField(
        read_only=True, source="sell_group.discount", default=0
    )

    class Meta:
        model = Sell
        fields = (
            "id",
            "shop_product",
            "seller__first_name",
            "extra_info",
            "quantity",
            "sell_price",
            "total_priced",
            "created_timestamp",
            "profits",
            "product_name",
            "sell_group",
            "discounts",
        )
        read_only_fields = (
            "id",
            "sell_group",
            "__str__",
        )

    def get_created_timestamp(self, object):
        return object.created_timestamp.strftime("%d-%h-%Y a las %I:%M %p")

    def validate(self, attrs):
        quantity = int(attrs.get("quantity"))
        shop_product = attrs.get("shop_product")
        if shop_product.quantity < quantity:
            raise serializers.ValidationError(
                "La cantidad solicitada es mayor que la disponibilidad."
            )
        return attrs

    def validate_quantity(self, value):
        if not value or value < 1:
            raise serializers.ValidationError(
                "La venta debe ser de al menos un elemento"
            )
        return value
