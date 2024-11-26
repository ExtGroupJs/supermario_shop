from rest_framework import viewsets

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.dashboard import (
    DashboardCountsSerializer,
    DashboardInvestmentSerializer,
    DashboardSerializer,
)

from django.db.models.functions import (
    TruncDay,
    TruncWeek,
    TruncMonth,
    TruncQuarter,
    TruncYear,
)
from django.db.models import F, ExpressionWrapper, FloatField


from apps.common.mixins.serializer_map import SerializerMapMixin

from rest_framework.decorators import action
from django.db.models import Count, Sum
from rest_framework.response import Response

from apps.common.permissions import CommonRolePermission
from apps.common.utils.allowed_frequencies import AllowedFrequencies


class DashboardViewSet(
    SerializerMapMixin,
    viewsets.ViewSet,
    # GenericAPIView,
):
    serializer_class = DashboardCountsSerializer

    @action(
        detail=False,
        methods=["POST"],
        url_name="shop-product-investment",
        url_path="shop-product-investment",
        serializer_class=DashboardInvestmentSerializer,
        permission_classes=[CommonRolePermission],
    )
    def shop_product_investment(self, request):
        """
        This function obtains the total investment for a given date limit, shop, product or a combination
        """
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)

        objects = ShopProducts.objects.filter(**serializer.validated_data)
        investments = 0
        for obj in objects:
            investments += obj.investment()
        return Response({"investments": investments})

    @action(
        detail=False,
        methods=["POST"],
        url_name="sell-profits",
        url_path="sell-profits",
        permission_classes=[CommonRolePermission],
    )
    def sell_profits(self, request):
        """
        This function obtains the total profits of sells, optionaly can be filtered by shop, product_shop, date, or a combination
        can be grouped for painting graphics or so in "day", "week", "month", "quarter" or "year"
        """
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        frequency = serializer.validated_data.pop("frequency", None)
        sell_objects = Sell.objects.filter(**serializer.validated_data).select_related(
            "sell_group"
        )
        sell_group_ids = (
            sell_objects.filter(sell_group__discount__gt=0)
            .values_list("sell_group_id", flat=True)
            .distinct()
        )
        sell_group_discounts = SellGroup.objects.filter(
            id__in=sell_group_ids,
        ).aggregate(Sum(F("discount")))
        if frequency:
            results = (
                sell_objects.annotate(
                    frequency=self._get_frequency_function_given_payload_string(
                        frequency
                    )("updated_timestamp")
                )
                .values("frequency")
                .annotate(
                    total=Sum(
                        ExpressionWrapper(
                            (
                                F("shop_product__sell_price")
                                - F("shop_product__cost_price")
                            )
                            * F("quantity"),
                            output_field=FloatField(),
                        )
                    )
                )
                .order_by("frequency")
            )
        else:
            tmp_queryset = sell_objects.annotate(
                total=Sum(
                    ExpressionWrapper(
                        (F("shop_product__sell_price") - F("shop_product__cost_price"))
                        * F("quantity"),
                        output_field=FloatField(),
                    )
                )
            ).values("total")
            results = {
                "frequency": "None",
                "total": sum(item["total"] for item in tmp_queryset),
            }
        result = {"result": results}
        has_discount = sell_group_discounts.get("discount__sum")
        if has_discount:
            result["discounts"] = has_discount
            result["sell_group_ids"] = list(sell_group_ids)
        else:
            result["discounts"] = 0

        return Response(result)

    @action(
        detail=False,
        methods=["POST"],
        url_name="shop-product-sells-count",
        url_path="shop-product-sells-count",
        permission_classes=[CommonRolePermission],
    )
    def shop_product_sells_count(self, request):
        """
        This function obtains the total quantity of sells, optionaly can be filtered by shop, product_shop, date, or a combination
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
                .annotate(total=Count("quantity"))
                .order_by("frequency")
            )
        else:
            results = {
                "frequency": "None",
                "total": len(objects.annotate(total=Count("quantity")).values("total")),
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
