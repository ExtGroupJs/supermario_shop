from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.business_app.models.sell import Sell
from django.db import transaction

from apps.business_app.sell_annotations import line_totals, product_name, profits
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
        .annotate(**line_totals())
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

        When the removed sell is the last one of its group, the group is removed
        too: an empty group has no product to render and would linger as a sale
        with nothing in it, so there is no note worth keeping either.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        sell_group = instance.sell_group
        with transaction.atomic():
            # ``exclude`` asks the database for the real remaining sells of the
            # group instead of trusting the instance loaded with the sell.
            is_last_sell = sell_group is not None and not sell_group.sells.exclude(
                pk=instance.pk
            ).exists()
            if not is_last_sell:
                serializer.mark_deleted_sell(instance)
            self.perform_destroy(instance)
            if is_last_sell:
                sell_group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = super().get_queryset()
        request_user = self.request.user if not self.request.user.is_anonymous else None

        if request_user.groups.filter(
            id__in=[Groups.SHOP_OWNER.value, Groups.SUPER_ADMIN.value]
        ).exists():
            queryset = queryset.annotate(profits=profits()).annotate(
                product_name=product_name(with_shop=True)
            )
        else:
            queryset = queryset.filter(
                shop_product__shop=SystemUser.objects.get(id=request_user.id).shop
            ).annotate(product_name=product_name())
        return queryset
