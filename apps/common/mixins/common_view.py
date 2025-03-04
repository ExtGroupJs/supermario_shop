from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import GenericAPIView

from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.filters import CommonFilter


class CommonViewMixin(GenericAPIView):
    """
    Use this as parent class in all views. Adds:
     - ordering
     - default filtering
    """

    # Filtering
    _filter_class = None
    ordering_fields = "__all__"
    ordering = ["-created_timestamp"]
    # filterset_fields = [field.name for field in queryset.model._meta.fields]
    filterset_class = CommonFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
