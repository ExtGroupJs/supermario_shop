from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup


from apps.business_app.serializers.sell_group import SellGroupSerializer
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.enums_mixin import EnumsMixin

from apps.common.permissions import SellViewSetPermission
from apps.users_app.models.groups import Groups
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

    # A group has no shop nor product of its own: it belongs to the shop of the
    # products it sold, so every product level lookup travels through the sells
    # relation. Those joins can match more than one sell of the same group, hence
    # the ``distinct()`` applied by ``get_queryset``.
    filterset_fields = {
        "for_date": ["gte", "lte", "date__gte", "date__lte", "date"],
        "created_timestamp": ["gte", "lte"],
        "seller": ["exact"],
        "client": ["exact"],
        "payment_method": ["exact"],
        "discount": ["exact"],
        "total": ["gte", "lte"],
        "sells__shop_product": ["exact"],
        "sells__shop_product__shop": ["exact"],
        "sells__shop_product__product": ["exact"],
        "sells__shop_product__product__model": ["exact"],
        "sells__shop_product__product__model__brand": ["exact"],
    }

    search_fields = [
        "id",
        "extra_info",
        "client__name",
        "client__phone",
        "seller__username",
        "sells__shop_product__product__name",
        "sells__shop_product__product__model__name",
        "sells__shop_product__product__model__brand__name",
    ]

    # Only columns of the model: ``sells`` and ``client_name`` are serializer
    # output (a reverse relation and a write only field), ordering by them makes
    # the database raise a FieldError instead of sorting anything.
    ordering_fields = (
        "id",
        "for_date",
        "seller",
        "client",
        "total",
        "discount",
        "payment_method",
        "created_timestamp",
        "updated_timestamp",
    )

    def get_queryset(self):
        """
        Groups with their seller, client and sells ready to be serialized.

        The listing serializes the sells of every group and the reports print the
        client name, so the joins are declared upfront instead of being queried
        row by row. ``distinct()`` is what keeps the joined search and filters
        (``sells__*``) from repeating a group once per matching sell.
        """
        return (
            SellGroup.objects.all()
            .select_related("client", "seller")
            .prefetch_related("sells")
            .distinct()
        )

    def _filter_by_shop(self, queryset, shop_id):
        """
        Narrow the sell groups down to the ones that belong to a shop.

        The shop is reached through the sells of the group, but the rows are still
        sell groups: the individual sells are never loaded nor counted, they only
        resolve which shop the group belongs to.
        """
        if not shop_id:
            return queryset
        return queryset.filter(sells__shop_product__shop=shop_id).distinct()

    def _scope_to_request_user(self, queryset, request):
        """
        Keep a seller inside its own shop, the way the sells listing does.

        Only applied by the period report, which is the endpoint that reports money:
        a seller must not add up another shop's sales by asking for another shop.
        """
        request_user = request.user if request.user else None
        if not request_user or request_user.is_anonymous:
            return queryset
        if request_user.groups.filter(
            id__in=[Groups.SUPER_ADMIN.value, Groups.SHOP_OWNER.value]
        ).exists():
            return queryset
        return self._filter_by_shop(queryset, request_user.shop_id)

    def _filter_by_period(self, queryset, start_date, end_date):
        """Keep the sell groups whose sale date falls inside the period."""
        queryset = queryset.filter(for_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(for_date__date__lte=end_date)
        return queryset

    @staticmethod
    def _today():
        """Today in the project timezone.

        ``timezone.localdate()`` only accepts aware datetimes, so it blows up under
        ``USE_TZ = False`` (this project runs naive datetimes). Converting only when
        the value is aware keeps it correct under both settings.
        """
        now = timezone.now()
        if timezone.is_aware(now):
            now = timezone.localtime(now)
        return now.date()

    @staticmethod
    def _parse_date(raw_value, default):
        """Read an ISO date from the query string, falling back to today."""
        if not raw_value:
            return default
        try:
            return datetime.strptime(raw_value, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _format_period(start_date, end_date):
        """Label of the period, shown on the first line of the report."""
        if start_date == end_date:
            return start_date.strftime("%d-%b-%Y")
        return f"{start_date.strftime('%d-%b-%Y')} al {end_date.strftime('%d-%b-%Y')}"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sells = serializer.validated_data.pop("sells")
        # The group and its sells are one single unit of work: creating the group
        # fires the signals that move the inventory, so a child sell failing half
        # way must not leave a group behind already charged against the stock.
        with transaction.atomic():
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
        # Every sell puts its quantity back through the post_delete signal, so the
        # sells, the inventory restores and the group removal succeed or fail
        # together instead of leaving a cancelled sale with its stock missing.
        with transaction.atomic():
            for sell in instance.sells.all():
                sell.delete()
            self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["GET"], url_path="report")
    def report(self, request, pk=None):
        """
        Plain text receipt of a sell group, the same one printed when the sale is made.

        The lines are rendered by the serializer because the sells listing annotations
        (sell price, product name) only exist in that endpoint queryset, so the report
        cannot be rebuilt from the group payload alone.
        """
        sell_group = self.get_object()
        return Response(
            {"report": self.get_serializer(sell_group).get_report(sell_group)}
        )

    @action(detail=True, methods=["GET"], url_path="warehouse-report")
    def warehouse_report(self, request, pk=None):
        """
        Warehouse receipt of a sell group: products and quantities, no money.

        It is built out of the same sells the sales receipt lists, but the client,
        the payment method and every amount are left out because this copy is only
        used to prepare the goods that leave the shop.
        """
        sell_group = self.get_object()
        return Response(
            {
                "report": self.get_serializer(sell_group).get_warehouse_report(
                    sell_group
                )
            }
        )

    @action(detail=False, methods=["GET"], url_path="period-report")
    def period_report(self, request):
        """
        Plain text summary of the sell groups of a period, with their net amount.

        The report is built out of the sell groups alone: no individual sell is loaded
        nor counted, each group contributes its stored total once. When no period is
        given it reports the sales of today.

        Both dates are inclusive and are compared against the sell group ``for_date``,
        so a group is never cut in half by the end of the period. A start date
        after the end date is rejected with a 400 instead of reporting nothing.
        """
        today = self._today()
        start_date = self._parse_date(request.query_params.get("start_date"), today)
        end_date = self._parse_date(request.query_params.get("end_date"), start_date)

        # A period that starts after it ends can never match anything, so it is
        # rejected instead of silently reporting an empty (and misleading) period.
        if start_date > end_date:
            return Response(
                {
                    "detail": (
                        "La fecha 'Ventas Desde' no puede ser mayor que la fecha "
                        "'Ventas Hasta'."
                    ),
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self._filter_by_period(
            self._filter_by_shop(
                self._scope_to_request_user(self.get_queryset(), request),
                request.query_params.get("shop"),
            ),
            start_date,
            end_date,
        ).order_by("for_date", "id")

        # Only the group level fields the report prints are read, so the individual
        # sells are never fetched no matter how many products the groups contain.
        sell_groups = list(
            queryset.annotate(
                client_name=Coalesce("client__name", Value("")),
                # ``payment_method`` viaja porque la linea del reporte lo imprime; si no
                # estuviera en el values() el dict no lo trae y la linea revienta.
            ).values(
                "id",
                "for_date",
                "total",
                "discount",
                "payment_method",
                "client_name",
            )
        )
        # ``sum`` starts at the int 0, so the empty period is coerced back to Decimal
        # to keep the report from having to deal with an int total.
        net_total = sum(
            (
                Decimal(str(group["total"] or 0)) - Decimal(str(group["discount"] or 0))
                for group in sell_groups
            ),
            Decimal("0.00"),
        )
        net_total = max(net_total, Decimal("0.00"))

        serializer = self.get_serializer()
        period = self._format_period(start_date, end_date)
        return Response(
            {
                "report": serializer.get_summary_report(sell_groups, period, net_total),
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "total": f"{net_total:.2f}",
                "groups": len(sell_groups),
            }
        )


class PaymentMethodsViewSet(EnumsMixin):
    items = (("payment_methods", SellGroup.PAYMENT_METODS),)
