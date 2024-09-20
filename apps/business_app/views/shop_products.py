from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.shop_products import (
    ReadShopProductsSerializer,
    ShopProductsSerializer,
)
from apps.common.views import CommonOrderingFilter, SerializerMapMixin


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
