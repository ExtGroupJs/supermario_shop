import django_filters
from decimal import Decimal, InvalidOperation

from django.db.models import Q
from apps.common.filters.generic_log import GenericLogFilter
from apps.common.models.generic_log import GenericLog


class ShopProductsLogsFilter(GenericLogFilter):
    entries = django_filters.BooleanFilter(
        field_name="entries", method="filter_entries"
    )
    shop = django_filters.NumberFilter(field_name="shop", lookup_expr="exact")

    class Meta(GenericLogFilter.Meta):
        fields = {
            "content_type": ["exact"],
            "object_id": ["exact"],
            "performed_action": ["exact"],
            "created_by": ["exact"],
            "created_timestamp": ["gte", "lte"],
        }

    @staticmethod
    def _as_decimal(value):
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return None

    def filter_entries(self, queryset, name, value):
        updated_logs = queryset.filter(performed_action=GenericLog.ACTION.UPDATED).only(
            "id", "details"
        )
        matching_updated_ids = []

        for log in updated_logs:
            quantity_changes = (log.details or {}).get("quantity") or {}
            old_value = self._as_decimal(quantity_changes.get("old_value"))
            new_value = self._as_decimal(quantity_changes.get("new_value"))

            if old_value is None or new_value is None:
                continue

            if value and new_value > old_value:
                matching_updated_ids.append(log.id)
            elif not value and new_value < old_value:
                matching_updated_ids.append(log.id)

        query = Q(id__in=matching_updated_ids)
        if value:
            query |= Q(performed_action=GenericLog.ACTION.CREATED)

        return queryset.filter(query)
