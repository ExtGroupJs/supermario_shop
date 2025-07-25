from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup


from apps.business_app.serializers.sell_group import SellGroupSerializer
from apps.business_app.serializers.sell_group_check_serializer import SellGroupCheckSerializer
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.enums_mixin import EnumsMixin

from apps.common.permissions import CommonRolePermission, SellViewSetPermission
from apps.users_app.models.system_user import SystemUser
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action


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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sells = serializer.validated_data.pop("sells")
        created_sell_group = self.perform_create(serializer)
        for sell in sells:
            sell["sell_group"] = created_sell_group
            sell["seller"] = created_sell_group.seller
            Sell.objects.create(**sell)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        return serializer.save(seller=SystemUser.objects.get(id=self.request.user.id))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        for sell in instance.sells.all():
            sell.delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[CommonRolePermission],
        url_name="sell-group-list-to-check",
        url_path="sell-group-list-to-check",
    )
    def sell_group_list_to_check(self, request, *args, **kwargs):
        instance = self.get_object()
        sells = instance.sells.all()
        product_names = [
            f"_{sell.quantity if sell.quantity > 1 else ''}{' ' if sell.quantity > 1 else ''}{sell.shop_product.product.name} {sell.shop_product.product.model.name}"
            for sell in sells
        ]
        words_to_replace = [
            "Engrand ",
            "Emgrand ",
        ]
        for word in words_to_replace:
            product_names = [product.replace(word, "") for product in product_names]

        return Response({"product_names": product_names})


    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[CommonRolePermission],
        serializer_class=SellGroupCheckSerializer,
        url_name="check-sell-group-list",
        url_path="check-group-list",
    )
    def check_sell_group_list(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        self_sells = serializer.validated_data.get("self_sells")
        whatsapp_sells = serializer.validated_data.get("whatsapp_sells")
        return Response({"product_names": ""})


class PaymentMethodsViewSet(EnumsMixin):
    items = (("payment_methods", SellGroup.PAYMENT_METODS),)
