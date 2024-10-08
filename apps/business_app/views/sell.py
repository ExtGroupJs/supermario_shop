from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.product import Product
from apps.business_app.models.sell import Sell
from apps.business_app.serializers.product import (
    ProductSerializer,
    ReadProductSerializer,
)
from apps.business_app.serializers.sell import SellSerializer
from apps.common.pagination import AllResultsSetPagination
from apps.common.views import CommonOrderingFilter, SerializerMapMixin
from apps.common.permissions import SellViewSetPermission
from apps.users_app.models.system_user import SystemUser


class SellViewSet(viewsets.ModelViewSet, GenericAPIView):
    queryset = Sell.objects.all().select_related("shop_product", "seller")
    serializer_class = SellSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    permission_classes = [SellViewSetPermission]
    filterset_fields = [
        "shop_product",
        "shop_product__product",
        "shop_product__product__model",
        "shop_product__product__model__brand",
        "seller",
    ]
    search_fields = [
        "shop_product__product__name",
        "shop_product__product__model__name",
        "shop_product__product__model__brand__name",
        "seller__username",
        "extra_info",
    ]
    def perform_create(self, serializer):
        serializer.save(seller=SystemUser.objects.get(id=self.request.user.id) )
