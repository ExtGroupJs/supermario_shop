from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, F, Value
from django.db.models.functions import Coalesce
from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.pallet import Pallet
from apps.business_app.serializers.pallet import PalletSerializer
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.permissions import CommonRolePermission


class PalletViewSet(viewsets.ModelViewSet, GenericAPIView):
    queryset = Pallet.objects.annotate(
        shop_name=F("shop__name"),
        shop_products_count=Coalesce(
            Count("shopproducts", distinct=True),
            Value(0),
        ),
    ).all()
    serializer_class = PalletSerializer
    permission_classes = [CommonRolePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    filterset_fields = [
        "shop",
        "rack",
        "section",
        "number",
    ]
    search_fields = [
        "shop__name",
        "section",
    ]
    ordering = ["rack", "section", "number"]
    ordering_fields = [
        "shop_name",
        "shop_products_count",
        "rack",
        "section",
        "number",
    ]
