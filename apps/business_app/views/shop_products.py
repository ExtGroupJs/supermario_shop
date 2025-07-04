from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.shop_products import (
    CatalogShopProductSerializer,
    MoveToAnotherShopSerializer,
    ReadShopProductsSerializer,
    ShopProductsSerializer,
)
from rest_framework.response import Response


from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.serializer_map import SerializerMapMixin

from apps.common.pagination import AllResultsSetPagination
from apps.common.permissions import CommonRolePermission, ShopProductsViewSetPermission
from rest_framework.permissions import AllowAny
from apps.users_app.models.groups import Groups
from apps.users_app.models.system_user import SystemUser
from rest_framework.decorators import action
from django.db.models import F, Value, Q, Sum
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
        .annotate(sales_count=Sum("sells__quantity"))
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

        request_user = self.request.user if not self.request.user.is_anonymous else None
        is_admin_or_owner = (
            request_user
            and request_user.groups
            and request_user.groups.filter(
                id__in=(
                    Groups.SUPER_ADMIN.value,
                    Groups.SHOP_OWNER.value,
                )
            ).exists()
        )
        filter_by_quantity = Q(quantity__gt=0) if not is_admin_or_owner else Q()
        filter_by_shop = (
            Q(shop=SystemUser.objects.get(id=request_user.id).shop)
            if request_user and not is_admin_or_owner
            else Q()
        )
        return queryset.filter(filter_by_quantity, filter_by_shop)

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

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[CommonRolePermission],  # TODO test for this
        serializer_class=MoveToAnotherShopSerializer,
        url_name="move-to-another-shop",
        url_path="move-to-another-shop",
    )
    def move_to_another_shop(self, request, *args, **kwargs):
        """
        Move a shop product to another shop.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        output_serializer = ReadShopProductsSerializer
        return Response(
            output_serializer(instance=instance, context={"request": request}).data
        )
