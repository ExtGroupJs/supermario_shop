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

from apps.common.pagination import AllResultsSetPagination
from apps.common.permissions import ShopProductsViewSetPermission
from apps.users_app.models.groups import Groups
from apps.users_app.models.system_user import SystemUser
from rest_framework.decorators import action
from django.db.models import Count, Sum
from rest_framework.response import Response


class ShopProductsViewSet(
    SerializerMapMixin,
    viewsets.ModelViewSet,
    GenericAPIView,
):
    queryset = ShopProducts.objects.all()
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
            if self.action == "list_for_sale":
                queryset =  queryset.filter(quantity__gt=0)
            return queryset
        system_user = SystemUser.objects.get(id=self.request.user.id)
        return queryset.filter(quantity__gt=0, shop=system_user.shop)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)
    @action(
        detail=False,
        methods=["GET"],
        url_name="list-for-sale",
        url_path="list-for-sale",
    )
    def list_for_sale(self, request):
        return self.list(request)
