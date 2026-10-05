from decimal import Decimal

from rest_framework import serializers

from apps.business_app.models.sell_group import SellGroup
from apps.business_app.serializers.sell import SellSerializer

two_decimals = Decimal("0.01")


class GroupSellLineSerializer(SellSerializer):
    """
    A single sell of a group, the one rendered inside the collapsible child row.

    It only keeps the sell level columns: everything about the sale as a whole
    (client, total, discount, note, date) already travels on the parent group row,
    so repeating it on every sell would only make the payload bigger.

    ``product_name``, ``sell_price``, ``total_priced`` and ``profits`` have no column
    behind them, they are database annotations. ``GroupSellViewSet`` has to prefetch
    the sells with them, otherwise those keys are simply missing from the payload and
    the child row would show empty cells.
    """

    class Meta(SellSerializer.Meta):
        fields = (
            "id",
            "shop_product",
            "seller__first_name",
            "extra_info",
            "quantity",
            "sell_price",
            "total_priced",
            "profits",
            "product_name",
            "created_timestamp",
        )


class GroupSellSerializer(serializers.ModelSerializer):
    """
    A sell group as the top level row of the group sells listing.

    This is the whole sale in one row: who it was sold to, when, for how much and
    what it contains. The sells travel nested under it instead of as rows of their
    own, so the page can fold them away without a second request.
    """

    sells = GroupSellLineSerializer(many=True, read_only=True)
    seller__first_name = serializers.CharField(
        source="seller.__str__", read_only=True, default=""
    )
    client_name = serializers.CharField(
        source="client.name", read_only=True, default=""
    )
    client_phone = serializers.CharField(
        source="client.phone", read_only=True, default=""
    )
    payment_method_label = serializers.CharField(source="get_payment_method_display")
    for_date_label = serializers.SerializerMethodField()
    net_total = serializers.SerializerMethodField()
    sells_count = serializers.SerializerMethodField()

    class Meta:
        model = SellGroup
        fields = (
            "id",
            "for_date",
            "for_date_label",
            "seller__first_name",
            "client",
            "client_name",
            "client_phone",
            "payment_method",
            "payment_method_label",
            "total",
            "discount",
            "net_total",
            "extra_info",
            "sells_count",
            "sells",
        )
        read_only_fields = fields

    def get_for_date_label(self, object):
        """
        The sale date already formatted for the table.

        It is the seller given ``for_date``, not the row creation timestamp: all the
        sells of a group share it, so a group is never shown with the date of one of
        its lines.
        """
        if not object.for_date:
            return ""
        return object.for_date.strftime("%d-%b-%Y %I:%M %p")

    def get_net_total(self, object): # TODO get in the queryset as an annotation
        """What the sale is actually worth, once the discount is taken off."""
        net = Decimal(object.total or 0) - Decimal(object.discount or 0)
        return max(net, Decimal("0.00")).quantize(two_decimals)

    def get_sells_count(self, object): # TODO get in the queryset as an annotation
        """
        How many products the group contains.

        It reads the prefetched sells instead of a ``Count`` annotation because the
        rows are already fetched and loaded for the child row; counting them again in
        the database would only repeat work that was already done.
        """
        return len(object.sells.all())
