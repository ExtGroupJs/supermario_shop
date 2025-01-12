import django_filters
from django.db.models import F, Q
from django.db.models.functions import Cast
from apps.common.filters.generic_log import GenericLogFilter
from apps.common.models.generic_log import GenericLog


class ShopProductsLogsFilter(GenericLogFilter):
    entries = django_filters.BooleanFilter(
        field_name="entries", method="filter_entries"
    )

    class Meta(GenericLogFilter.Meta):
        fields = {
            "content_type": ["exact"],
            "object_id": ["exact"],
            "performed_action": ["exact"],
            "created_by": ["exact"],
            "created_timestamp": ["date__gte", "date__lte"],
        }

    def filter_entries(self, queryset, name, value):
        if value:
            filter_content = Q(
                details__quantity__new_value__gt=F("details__quantity__old_value")
            )

        else:
            filter_content = Q(
                details__quantity__new_value__lt=F("details__quantity__old_value")
            )
        return_queryset = queryset.filter(
            Q(performed_action=GenericLog.ACTION.UPDATED) & filter_content
        )
        if value:
            return_queryset = return_queryset.union(
                queryset.filter(performed_action=GenericLog.ACTION.CREATED)
            )

        return return_queryset
