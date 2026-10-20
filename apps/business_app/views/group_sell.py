from django.db.models import DecimalField, ExpressionWrapper, F, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins
from rest_framework.viewsets import GenericViewSet

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.sell_annotations import line_totals, product_name, profits
from apps.business_app.serializers.group_sell import GroupSellSerializer
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.permissions import SellViewSetPermission
from apps.users_app.models.groups import Groups
from apps.users_app.models.system_user import SystemUser


class GroupSellViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    Sell groups as the top level rows, with their sells nested under each group.

    It is the same screen as the sells listing with a different unit: there a sell is
    a row and the DataTables rowGroup plugin folds the groups, here a group is a row
    and its sells are the child rows. The page can therefore collapse a sale without
    asking again, and the payload carries the group data once instead of repeating it
    on every sell of the group.

    Read only on purpose: creating and cancelling a sale goes through the sell groups
    and sell products endpoints, which is where those rules already live.
    """

    serializer_class = GroupSellSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    permission_classes = [SellViewSetPermission]

    # The dates filter the ``for_date`` of the group, which is the date the seller
    # gave the sale. The shop is reached through the sells of the group because a
    # group itself has no shop: a group belongs to the shop of its products.
    filterset_fields = {
        "for_date": ["gte", "lte", "date__gte", "date__lte", "date"],
        "seller": ["exact"],
        "client": ["exact"],
        "total": ["gte", "lte"],
        "discount": ["exact"],
        "sells__shop_product__shop": ["exact"],
        "sells__shop_product__product__model__brand": ["exact"],
    }
    search_fields = [
        "extra_info",
        "client__name",
        "client__phone",
        "seller__username",
        "sells__shop_product__product__name",
    ]
    # ``net_total`` is annotated by the queryset so it can be sorted by; the other
    # columns of the row (``client_name``, ``sells_count``, the formatted labels) are
    # serializer output and have nothing to sort on in the database.
    ordering_fields = (
        "id",
        "for_date",
        "seller",
        "client",
        "total",
        "discount",
        "net_total",
    )

    def _sees_every_shop(self):
        """Owners and admins see all the shops, a seller only sees its own."""
        request_user = self.request.user if self.request.user else None
        if not request_user or request_user.is_anonymous:
            return False
        return request_user.groups.filter(
            id__in=[Groups.SUPER_ADMIN.value, Groups.SHOP_OWNER.value]
        ).exists()

    def _sells_queryset(self):
        """
        The sells of a group, annotated with the columns the child row renders.

        ``GroupSellLineSerializer`` reads ``product_name``, ``sell_price``,
        ``total_priced`` and ``profits`` off the sell, and none of them is a column
        of ``Sell``: they only exist while the database builds the queryset. Reading
        ``group.sells.all()`` without this prefetch would run a plain query, those
        four keys would be missing from the payload and every child row would render
        an empty product, price and amount. So the prefetch has to carry them.
        """
        return (
            Sell.objects.all()
            .select_related("shop_product", "seller")
            .annotate(**line_totals())
            .annotate(profits=profits())
            .annotate(product_name=product_name(with_shop=self._sees_every_shop()))
        )

    def get_queryset(self):
        queryset = (
            SellGroup.objects.all()
            .filter(sells__isnull=False)
            .select_related("client", "seller")
            .prefetch_related(Prefetch("sells", queryset=self._sells_queryset()))
            .annotate(
                net_total=ExpressionWrapper(
                    F("total") - F("discount"), output_field=DecimalField()
                )
            )
        )

        if self._sees_every_shop():
            return queryset.distinct()

        # A seller is kept inside its own shop, the way the sells listing does, so it
        # cannot read another shop's sales by asking for another shop.
        request_user = self.request.user
        return queryset.filter(
            sells__shop_product__shop=SystemUser.objects.get(id=request_user.id).shop
        ).distinct()
