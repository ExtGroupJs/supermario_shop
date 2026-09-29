from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView
from apps.business_app.models.brand import Brand
from apps.business_app.serializers.brand import BrandSerializer
from apps.business_app.utils.catalog_shop import (
    brand_ids_in_stock,
    resolve_catalog_shop_id,
)
from django_filters.rest_framework import DjangoFilterBackend

from apps.common.common_ordering_filter import CommonOrderingFilter

from apps.common.permissions import CommonRolePermission
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

SHOP_FILTER_PARAM = "model__product__shopproducts__shop"


class BrandViewSet(viewsets.ModelViewSet, GenericAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [CommonRolePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    filterset_fields = [
        SHOP_FILTER_PARAM,
    ]

    search_fields = [
        "name",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "catalog":
            shop_id = resolve_catalog_shop_id(self.request, SHOP_FILTER_PARAM)
            if shop_id is None:
                return queryset.none()
            # Only brands with something actually sellable in the shop.
            queryset = queryset.filter(id__in=brand_ids_in_stock(shop_id))
        return queryset

    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def catalog(self, request):
        return self.list(request)
