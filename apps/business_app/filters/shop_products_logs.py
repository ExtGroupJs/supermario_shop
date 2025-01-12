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
            "created_timestamp": ["gte", "lte"],
        }

    def filter_entries(self, queryset, name, value):
        extra_condition = Q()
        if value:
            filter_content = Q(
                details__quantity__new_value__gt=F("details__quantity__old_value")
            )
            extra_condition = Q(performed_action=GenericLog.ACTION.CREATED)
        else:
            filter_content = Q(
                details__quantity__new_value__lt=F("details__quantity__old_value")
            )
        return_queryset = queryset.filter(
            Q(Q(performed_action=GenericLog.ACTION.UPDATED) & filter_content)
            | extra_condition
        )

        return return_queryset
