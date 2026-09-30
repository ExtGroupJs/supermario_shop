from decimal import Decimal

from django.utils import timezone
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
    # Group level data used to build the sales table group header.
    client_name = serializers.CharField(
        read_only=True, source="sell_group.client.name", default=""
    )
    client_phone = serializers.CharField(
        read_only=True, source="sell_group.client.phone", default=""
    )
    group_total = serializers.DecimalField(
        read_only=True, source="sell_group.total", max_digits=10, decimal_places=2
    )
    group_extra_info = serializers.CharField(
        read_only=True, source="sell_group.extra_info", default=""
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
            "client_name",
            "client_phone",
            "group_total",
            "group_extra_info",
        )
        read_only_fields = (
            "id",
            "sell_group",
            "__str__",
        )

    def get_created_timestamp(self, object):
        return object.created_timestamp.strftime("%d-%h-%Y a las %I:%M %p")

    @staticmethod
    def _get_cancellation_label(shop_product, when):
        """Build the 'BORRADO <product> <day> <date>' note for a removed sell."""
        product = getattr(shop_product, "product", None)
        product_name = product.__str__() if product is not None else ""
        return f"BORRADO {product_name} {when.strftime('%d-%b-%Y')}".strip()

    def mark_deleted_sell(self, instance, when=None):
        """
        Leave a trace in the sell group before the sell row itself is hard deleted.

        Sell has no soft delete, so once the row is gone its own extra_info is gone
        too. The group survives and is what the sales table header renders as
        'Nota:', so the cancellation note is appended there. The group total is
        reduced by the same amount that the removed sell was contributing, otherwise
        the header would keep announcing an amount the shop no longer billed.

        The caller is responsible for deleting the instance, and for doing both
        inside a transaction when atomicity matters.
        """
        when = when or timezone.now()

        sell_group = instance.sell_group
        if sell_group is None:
            return

        amount = Decimal(instance.quantity) * Decimal(str(instance.shop_product.sell_price or 0))

        note = self._get_cancellation_label(instance.shop_product, when)
        previous_info = (sell_group.extra_info or "").strip()
        sell_group.extra_info = f"{previous_info}\n{note}" if previous_info else note
        sell_group.total = max(Decimal(sell_group.total or 0) - amount, Decimal("0.00"))
        # updated_timestamp is auto_now, so it is refreshed on every save.
        sell_group.save(update_fields=["extra_info", "total", "updated_timestamp"])

    def validate(self, attrs):
        quantity = int(attrs.get("quantity"))
        shop_product = attrs.get("shop_product")
        if shop_product.quantity < quantity:
            raise serializers.ValidationError(
                "La cantidad solicitada es mayor que la disponibilidad."
            )
        return attrs

    def validate_quantity(self, value):
        if not value:
            raise serializers.ValidationError(
                "La venta debe ser de al menos un elemento"
            )
        return value
