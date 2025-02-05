from datetime import timedelta
from django.db.models.functions import Now

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.shop_products import (
    CatalogShopProductSerializer,
    ReadShopProductsSerializer,
    ShopProductsSerializer,
)

from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.serializer_map import SerializerMapMixin

from apps.common.pagination import AllResultsSetPagination
from apps.common.permissions import ShopProductsViewSetPermission
from rest_framework.permissions import AllowAny
from apps.users_app.models.groups import Groups
from apps.users_app.models.system_user import SystemUser
from rest_framework.decorators import action
from django.db.models import Case, When, Value, BooleanField, F
from rest_framework.response import Response
from django.db.models.functions import Concat


class ShopProductsViewSet(
    SerializerMapMixin,
    viewsets.ModelViewSet,
    GenericAPIView,
):
    serializer_class = ShopProductsSerializer
    list_serializer_class = ReadShopProductsSerializer
    retrieve_serializer_class = ReadShopProductsSerializer
    pagination_class = AllResultsSetPagination
    permission_classes = [ShopProductsViewSetPermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    one_month_ago = Now() - timedelta(days=30)

    queryset = (
        ShopProducts.objects.all()
        .annotate(shop_name=F("shop__name"))
        .annotate(
            product_name=Concat(
                F("product__name"),
                Value(" ("),
                F("product__model__brand__name"),
                Value(" - "),
                F("product__model__name"),
                Value(") "),
            )
        )
        .annotate(
            is_new=Case(
                When(updated_timestamp__gte=one_month_ago, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )
    )
    filterset_fields = {
        "shop": ["exact"],
        "product": ["exact"],
        "product__model": ["exact"],
        "product__model__brand": ["exact"],
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
        "product__model__name",
        "product__model__brand__name",
    ]
    ordering = ["shop_name"]
    ordering_fields = [
        "product_name",
        "shop_name",
        "extra_info",
        "quantity",
        "cost_price",
        "sell_price",
        "updated_timestamp",
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
            if self.action in ("list_for_sale",):
                queryset = queryset.filter(quantity__gt=0)
            return queryset
        if self.request.user.pk:
            system_user = SystemUser.objects.get(id=self.request.user.pk)
            queryset = queryset.filter(shop=system_user.shop)
        return queryset.filter(quantity__gt=0)

    @action(
        detail=False,
        methods=["GET"],
        url_name="list-for-sale",
        url_path="list-for-sale",
        serializer_class=ReadShopProductsSerializer,
    )
    def list_for_sale(self, request):
        return self.list(request)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[AllowAny],
        serializer_class=CatalogShopProductSerializer,
    )
    def catalog(self, request):
        return self.list(request)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[AllowAny],
        serializer_class=CatalogShopProductSerializer,
        url_name="catalog-shop-product-detail",
        url_path="catalog-shop-product-detail",
    )
    def catalog_shop_product_detail(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
