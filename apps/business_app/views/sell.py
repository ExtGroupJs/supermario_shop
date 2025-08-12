from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.business_app.models.sell import Sell
from django.db.models import Value, F
from django.db.models.functions import Concat

from apps.business_app.serializers.sell import SellSerializer

from apps.common.common_ordering_filter import CommonOrderingFilter

from apps.common.permissions import SellViewSetPermission
from apps.users_app.models.system_user import SystemUser
from apps.users_app.models.groups import Groups
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class SellViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = (
        Sell.objects.all()
        .select_related("shop_product", "seller", "sell_group")
        .annotate(total_priced=F("quantity") * F("shop_product__sell_price"))
        .annotate(sell_price=F("shop_product__sell_price"))
    )
    serializer_class = SellSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    permission_classes = [SellViewSetPermission]
    filterset_fields = {
        "shop_product": ["exact"],
        "shop_product__shop": ["exact"],
        "seller": ["exact"],
        "shop_product__product": ["exact"],
        "shop_product__product__model": ["exact"],
        "shop_product__product__model__brand": ["exact"],
        "shop_product__sell_price": ["gte", "lte", "exact"],
        "quantity": ["gte", "lte", "exact"],
        "created_timestamp": ["gte", "lte"],
        "updated_timestamp": ["gte", "lte"],
    }

    search_fields = [
        "shop_product__product__name",
        "shop_product__product__model__name",
        "shop_product__product__model__brand__name",
        "seller__username",
        "extra_info",
    ]

    ordering_fields = SellSerializer.Meta.fields

    def perform_create(self, serializer):
        serializer.save(seller=SystemUser.objects.get(id=self.request.user.id))

    def get_queryset(self):
        queryset = super().get_queryset()
        request_user = self.request.user if not self.request.user.is_anonymous else None

        product_name = Concat(
            F("shop_product__product__name"),
            Value(" ("),
            F("shop_product__product__model__brand__name"),
            Value(" - "),
            F("shop_product__product__model__name"),
            Value(") "),
        )
        if request_user.groups.filter(
            id__in=[Groups.SHOP_OWNER.value, Groups.SUPER_ADMIN.value]
        ).exists():
            queryset = queryset.annotate(
                profits=(F("shop_product__sell_price") - F("shop_product__cost_price"))
                * F("quantity")
            ).annotate(
                product_name=Concat(
                    product_name,
                    Value(" - "),
                    F("shop_product__shop__name"),
                )
            )
        else:
            queryset = queryset.filter(
                shop_product__shop=SystemUser.objects.get(id=request_user.id).shop
            ).annotate(product_name=product_name)
        return queryset
