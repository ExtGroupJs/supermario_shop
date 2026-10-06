from rest_framework import viewsets

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.sell_annotations import profits
from apps.business_app.serializers.dashboard import (
    DashboardCountsSerializer,
    DashboardSellGroupSerializer,
)

from django.db.models.functions import (
    TruncDay,
    TruncWeek,
    TruncMonth,
    TruncQuarter,
    TruncYear,
)
from django.db.models import Count, ExpressionWrapper, FloatField, Sum


from apps.common.mixins.serializer_map import SerializerMapMixin

from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import CommonRolePermission
from apps.common.utils.allowed_frequencies import AllowedFrequencies

# Field of the sell group the dashboard measures the period by. The dashboard counts
# sales, and a sale is the group, so the day it belongs to is the day the group was
# registered, not the moment one of its sells was created or last edited.
SELL_GROUP_DATE_FIELD = "created_timestamp"


class DashboardViewSet(
    SerializerMapMixin,
    viewsets.ViewSet,
    # GenericAPIView,
):
    """Metrics of the home dashboard, all of them counted in sell groups.

    A sell group is the unit a sale is actually made of: a sale of five products is one
    sale, not five. So the tiles report groups, filter them by the group date and take
    the discount of a group once, and the sells are only summed when the money has to be
    read line by line (the profit, which no group stores).
    """

    serializer_class = DashboardCountsSerializer
    # The tiles measure groups, so they read a payload validated against the group
    # fields. ``SerializerMapMixin`` picks the serializer by action name, which is why
    # this cannot stay a single ``serializer_class`` for the whole viewset.
    sell_profits_serializer_class = DashboardSellGroupSerializer
    shop_product_sells_count_serializer_class = DashboardSellGroupSerializer

    def _sell_groups(self, request):
        """The sell groups the payload selects, and the frequency it asks to group by.

        Both filters are resolved against the group. The shop is the only awkward one:
        a group has no shop of its own, it is reached through the sells of the group,
        and that traversal is done with a subquery on purpose. Filtering with a join
        would repeat the group once per sell of the shop and every total built on top of
        it would be counted as many times as the group has lines.
        """
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)

        frequency = serializer.validated_data.pop("frequency", None)
        shop = serializer.validated_data.pop("shop", None)
        start_date = serializer.validated_data.pop("created_timestamp__gte", None)
        end_date = serializer.validated_data.pop("created_timestamp__lte", None)

        groups = SellGroup.objects.all()
        # The tiles send plain calendar dates and both ends are meant to be inclusive,
        # so the comparison goes through ``__date``: compared as a timestamp, the end
        # date would mean midnight and a sale made during that day (a sale of the 31st,
        # say) would fall out of the month it belongs to.
        if start_date:
            groups = groups.filter(
                **{f"{SELL_GROUP_DATE_FIELD}__date__gte": start_date}
            )
        if end_date:
            groups = groups.filter(**{f"{SELL_GROUP_DATE_FIELD}__date__lte": end_date})
        if shop is not None:
            groups = groups.filter(
                pk__in=Sell.objects.filter(shop_product__shop=shop).values(
                    "sell_group_id"
                )
            )
        return groups, frequency

    @staticmethod
    def _group_profit_expression():
        """Profit of a sell line: what it earns once the cost price is taken off.

        The margin lives on the price of each product, so it can only be read line by
        line, and that is the one thing the dashboard still asks the sells for. The
        expression itself is not written here: ``sell_annotations`` already builds it
        once for the sells and the group sells listings, so there is a single place
        where the margin is defined.
        """
        return ExpressionWrapper(profits(), output_field=FloatField())

    @action(
        detail=False,
        methods=["POST"],
        url_name="sell-profits",
        url_path="sell-profits",
        serializer_class=DashboardSellGroupSerializer,
        permission_classes=[CommonRolePermission],
    )
    def sell_profits(self, request):
        """
        Profit of the sell groups of a period, optionally filtered by shop and grouped
        for painting the graphics in "day", "week", "month", "quarter" or "year".

        A group stores the gross total and the discount but not the margin, so the money
        is still read line by line while the period and the grouping belong to the group:
        every line is dated with the group it belongs to, which is what keeps a group
        whole inside the bucket it was registered in.
        """
        groups, frequency = self._sell_groups(request)
        sell_objects = Sell.objects.filter(sell_group_id__in=groups.values("pk"))
        if frequency:
            results = (
                sell_objects.annotate(
                    frequency=self._get_frequency_function_given_payload_string(
                        frequency
                    )(f"sell_group__{SELL_GROUP_DATE_FIELD}")
                )
                .values("frequency")
                .annotate(total=Sum(self._group_profit_expression()))
                .order_by("frequency")
            )
        else:
            tmp_queryset = sell_objects.aggregate(
                total=Sum(self._group_profit_expression())
            )
            results = {
                "frequency": "None",
                "total": tmp_queryset.get("total"),
            }
        result = {"result": results}
        # The discount is a property of the group, so it is taken from the same groups
        # the profit was built on: once per sale, never once per line.
        discounted_groups = groups.filter(discount__gt=0)
        total_discount = discounted_groups.aggregate(total=Sum("discount")).get("total")
        if total_discount:
            result["discounts"] = total_discount
            result["sell_group_ids"] = list(
                discounted_groups.values_list("id", flat=True)
            )
        else:
            result["discounts"] = 0

        return Response(result)

    @action(
        detail=False,
        methods=["POST"],
        url_name="sell-group-totals",
        url_path="sell-group-totals",
        serializer_class=DashboardSellGroupSerializer,
        permission_classes=[CommonRolePermission],
    )
    def sell_group_totals(self, request):
        """
        Totales brutos de los grupos de venta (SellGroup.total), agrupados por
        frecuencia usando la fecha de creación del grupo.

        No suma líneas de venta: toma directamente el campo `total` de cada
        SellGroup. Esto es lo que deben mostrar las gráficas.
        """
        groups, frequency = self._sell_groups(request)

        if frequency:
            results = (
                groups.annotate(
                    frequency=self._get_frequency_function_given_payload_string(
                        frequency
                    )(SELL_GROUP_DATE_FIELD)
                )
                .values("frequency")
                .annotate(total=Sum("total") - Sum("discount"))
                .order_by("frequency")
            )
        else:
            tmp_queryset = groups.aggregate(total=Sum("total") - Sum("discount"))
            results = {
                "frequency": "None",
                "total": tmp_queryset.get("total"),
            }

        result = {"result": results}
        discounted_groups = groups.filter(discount__gt=0)
        total_discount = discounted_groups.aggregate(total=Sum("discount")).get("total")
        if total_discount:
            result["discounts"] = total_discount
            result["sell_group_ids"] = list(
                discounted_groups.values_list("id", flat=True)
            )
        else:
            result["discounts"] = 0

        return Response(result)

    @action(
        detail=False,
        methods=["POST"],
        url_name="shop-product-sells-count",
        url_path="shop-product-sells-count",
        serializer_class=DashboardSellGroupSerializer,
        permission_classes=[CommonRolePermission],
    )
    def shop_product_sells_count(self, request):
        """
        How many sales happened in a period, optionally filtered by shop and grouped for
        painting the graphics in "day", "week", "month", "quarter" or "year".

        One group is one sale, however many products it carries, which is the number the
        tiles report. Counting the sells of the group instead would report the sale of
        five products as five sales, and a sale whose products were entered one by one
        would keep changing its number as they are edited.
        """
        groups, frequency = self._sell_groups(request)
        if frequency:
            results = (
                groups.annotate(
                    frequency=self._get_frequency_function_given_payload_string(
                        frequency
                    )(SELL_GROUP_DATE_FIELD)
                )
                .values("frequency")
                .annotate(total=Count("pk"))
                .order_by("frequency")
            )
        else:
            results = {
                "frequency": "None",
                "total": groups.count(),
            }

        return Response({"result": results})

    @action(
        detail=False,
        methods=["POST"],
        url_name="shop-product-sell-products-count",
        url_path="shop-product-sell-products-count",
        permission_classes=[CommonRolePermission],
    )
    def shop_product_sells_products_count(self, request):
        """
        This function obtains the total quantity of selled products, optionaly can be filtered by shop, product_shop, date, or a combination
        can be grouped for painting graphics or so in "day", "week", "month", "quarter" or "year"
        """
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        frequency = serializer.validated_data.pop("frequency", None)
        objects = Sell.objects.filter(**serializer.validated_data)
        if frequency:
            results = (
                objects.annotate(
                    frequency=self._get_frequency_function_given_payload_string(
                        frequency
                    )("updated_timestamp")
                )
                .values("frequency")
                .annotate(total=Sum("quantity"))
                .order_by("frequency")
            )
        else:
            tmp_queryset = objects.annotate(total=Sum("quantity")).values("total")
            results = {
                "frequency": "None",
                "total": sum(item["total"] for item in tmp_queryset),
            }

        return Response({"result": results})

    def _get_frequency_function_given_payload_string(self, frequency):
        if frequency == AllowedFrequencies.DAY:
            return TruncDay
        if frequency == AllowedFrequencies.WEEK:
            return TruncWeek
        if frequency == AllowedFrequencies.MONTH:
            return TruncMonth
        if frequency == AllowedFrequencies.QUARTER:
            return TruncQuarter
        if frequency == AllowedFrequencies.YEAR:
            return TruncYear
