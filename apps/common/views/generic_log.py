from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.models.generic_log import GenericLog
from apps.common.pagination import AllResultsSetPagination
from apps.common.permissions import CommonRolePermission
from apps.common.serializers.generic_log import GenericLogSerializer


class GenericLogViewSet(viewsets.ReadOnlyModelViewSet, GenericAPIView):
    queryset = GenericLog.objects.all()
    serializer_class = GenericLogSerializer
    permission_classes = [CommonRolePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    pagination_class = AllResultsSetPagination
    filterset_fields = [
        "content_type",
        "object_id",
        "performed_action",
    ]
    search_fields = [
        "name",
        "description",
    ]
