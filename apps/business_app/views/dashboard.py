from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.sell import Sell
from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.dashboard import (
    DashboardInvestmentSerializer,
    DashboardSerializer,
)
from apps.business_app.serializers.shop_products import (
    ReadShopProductsSerializer,
    ShopProductsSerializer,
)

from django.db.models.functions import (
    TruncDay,
    TruncWeek,
    TruncMonth,
    TruncQuarter,
    TruncYear,
)


from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.serializer_map import SerializerMapMixin

from apps.common.pagination import AllResultsSetPagination
from apps.users_app.models.groups import Groups
from apps.users_app.models.system_user import SystemUser
from rest_framework.decorators import action
from django.db.models import Count, Sum
from rest_framework.response import Response


class DashboardViewSet(
    SerializerMapMixin,
    viewsets.ViewSet,
    # GenericAPIView,
):
    serializer_class = DashboardSerializer

    @action(
        detail=False,
        methods=["POST"],
        url_name="shop-product-investment",
        url_path="shop-product-investment",
        serializer_class=DashboardInvestmentSerializer,
    )
    def shop_product_investment(self, request):
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
        url_name="shop-product-sell-count",
        url_path="shop-product-sells-count",
    )
    def shop_product_sells_count(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        frequency = serializer.validated_data.pop("frequency", None)
        objects = Sell.objects.filter(**serializer.validated_data)
        if frequency:
            if frequency == "day":
                function_to_apply = TruncDay
            if frequency == "week":
                function_to_apply = TruncWeek
            if frequency == "month":
                function_to_apply = TruncMonth
            if frequency == "quarter":
                function_to_apply = TruncQuarter
            if frequency == "year":
                function_to_apply = TruncYear
            results = (
                objects.annotate(frequency=function_to_apply("updated_timestamp"))
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
