import django_filters

from apps.common.models.generic_log import GenericLog


class GenericLogFilter(django_filters.FilterSet):
    class Meta:
        model = GenericLog
        fields = {
            "content_type": ["exact"],
            "object_id": ["exact"],
            "performed_action": ["exact"],
            "created_by": ["exact"],
            "created_timestamp": ["date__gte", "date__lte"],
        }
