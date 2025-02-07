from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup



from apps.business_app.serializers.sell_group import SellGroupSerializer
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.enums_mixin import EnumsMixin

from apps.common.permissions import SellViewSetPermission
from apps.users_app.models.system_user import SystemUser
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status


class SellGroupViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = SellGroup.objects.all()
    serializer_class = SellGroupSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    permission_classes = [SellViewSetPermission]
    filterset_fields = {
        # "shop_product": ["exact"],
        # "seller": ["exact"],
        # "shop_product__product": ["exact"],
        # "shop_product__product__model": ["exact"],
        # "shop_product__product__model__brand": ["exact"],
        # "shop_product__sell_price": ["gte", "lte", "exact"],
        # "quantity": ["gte", "lte", "exact"],
        # "created_timestamp": ["gte", "lte"],
        # "updated_timestamp": ["gte", "lte"],
    }

    search_fields = [
        # "shop_product__product__name",
        # "shop_product__product__model__name",
        # "shop_product__product__model__brand__name",
        # "seller__username",
        # "extra_info",
    ]

    ordering_fields = SellGroupSerializer.Meta.fields

    def create(self, request, *args, **kwargs):
        seller = SystemUser.objects.get(id=request.user.id)
        request.data["seller"] = seller
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sells = serializer.validated_data.pop("sells")
        created_sell_group = self.perform_create(serializer)
        for sell in sells:
            sell["sell_group"] = created_sell_group
            sell["seller"] = seller
            Sell.objects.create(**sell)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        return serializer.save(seller=SystemUser.objects.get(id=self.request.user.id))


class PaymentMethodsViewSet(EnumsMixin):
    items = (("payment_methods", SellGroup.PAYMENT_METODS),)
