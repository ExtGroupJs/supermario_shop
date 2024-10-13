from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.shop_products import (
    ReadShopProductsSerializer,
    ShopProductsSerializer,
)
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.serializer_map import SerializerMapMixin
from apps.users_app.models.groups import Groups
from apps.users_app.models.system_user import SystemUser


class ShopProductsViewSet(
    SerializerMapMixin,
    viewsets.ModelViewSet,
    GenericAPIView,
):
    queryset = ShopProducts.objects.all()
    serializer_class = ShopProductsSerializer
    list_serializer_class = ReadShopProductsSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    filterset_fields = {
        "shop": ["exact"],
        "product": ["exact"],
        "quantity": ["gte", "lte", "exact"],
        "cost_price": ["gte", "lte", "exact"],
        "sell_price": ["gte", "lte", "exact"],
        "created_timestamp": ["gte", "lte"],
        "updated_timestamp": ["gte", "lte"],
    }

    search_fields = [
        "extra_info",
        "shop__name",
        "product__name",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        if (
            self.request.user.groups
            and self.request.user.groups.filter(
                id__in=(
                    Groups.SUPER_ADMIN.value,
                    Groups.SHOP_OWNER.value,
                )
            ).exists()
        ):
            return queryset
        system_user = SystemUser.objects.get(id=self.request.user.id)
        return queryset.filter(quantity__gt=0, shop=system_user.shop)
