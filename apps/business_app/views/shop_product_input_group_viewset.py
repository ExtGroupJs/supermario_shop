from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.business_app.models.sell_group import SellGroup


from apps.business_app.models.shop_product_input_group_model import (
    ShopProductInputGroup,
)
from apps.business_app.models.shop_product_input_model import ShopProductInput

from apps.business_app.serializers.shop_product_input_group_serializer import (
    ShopProductInputGroupSerializer,
)
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.enums_mixin import EnumsMixin

from apps.common.permissions import (
    ShopProductInputGroupViewSetPermission,
)
from apps.users_app.models.system_user import SystemUser
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status


class ShopProductInputGroupViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = ShopProductInputGroup.objects.all()
    serializer_class = ShopProductInputGroupSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    permission_classes = [ShopProductInputGroupViewSetPermission]

    filterset_fields = {
        # "shop_product__sell_price": ["gte", "lte", "exact"],
    }

    search_fields = [
        # "shop_product__product__name",
        # "extra_info",
    ]

    ordering_fields = ShopProductInputGroupSerializer.Meta.fields

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shop_products_input = serializer.validated_data.pop("shop_products_input")
        created_shop_product_input_group = self.perform_create(serializer)
        for input in shop_products_input:
            input["shop_product_input_group"] = created_shop_product_input_group
            input["author"] = created_shop_product_input_group.author
            ShopProductInput.objects.create(**input)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        return serializer.save(author=SystemUser.objects.get(id=self.request.user.id))


class PaymentMethodsViewSet(EnumsMixin):
    items = (("payment_methods", SellGroup.PAYMENT_METODS),)
