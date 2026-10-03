from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.business_app.models.sell import Sell
from django.db import transaction
from django.db.models import Value, F
from django.db.models.functions import Concat, Coalesce

from apps.business_app.serializers.sell import SellSerializer

from apps.common.common_ordering_filter import CommonOrderingFilter

from apps.common.permissions import SellViewSetPermission
from apps.users_app.models.system_user import SystemUser
from apps.users_app.models.groups import Groups
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
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
        .prefetch_related("sell_group")
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

    def destroy(self, request, *args, **kwargs):
        """
        Remove the sell from the listing and keep a trace of it in its group.

        The note and the total adjustment are applied by the serializer before the
        row is deleted, because the deleted sell can no longer report its own
        product, price and group. Both writes and the delete share one transaction
        so a failure cannot leave a group annotated for a sale that still exists.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        with transaction.atomic():
            serializer.mark_deleted_sell(instance)
            self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
                profits=(
                    F("shop_product__sell_price")
                    - Coalesce(F("shop_product__cost_price"), 0.0)
                )
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
