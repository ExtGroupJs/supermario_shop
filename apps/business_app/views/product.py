from django.db.models import F, Prefetch, Value
from django.db.models.functions import Concat
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.product import Product
from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.product import (
    ProductSerializer,
    ReadProductSerializer,
)
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.serializer_map import SerializerMapMixin
from apps.common.pagination import AllResultsSetPagination
from apps.common.permissions import CommonRolePermission


class ProductViewSet(SerializerMapMixin, viewsets.ModelViewSet, GenericAPIView):
    queryset = Product.objects.prefetch_related(
        Prefetch(
            "shopproducts_set",
            queryset=ShopProducts.objects.filter(
                deleted__isnull=True, shop__enabled=True
            ).select_related("shop"),
        )
    ).annotate(
        model_name=Concat(F("model__brand__name"), Value(" - "), F("model__name"))
    )
    serializer_class = ProductSerializer
    list_serializer_class = ReadProductSerializer
    permission_classes = [CommonRolePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    pagination_class = AllResultsSetPagination
    filterset_fields = [
        "model",
        "model__brand",
    ]
    search_fields = [
        "name",
        "description",
        "model__brand__name",
        "model__name",
    ]
    ordering = ["name"]
    ordering_fields = ["name", "model_name", "description"]
