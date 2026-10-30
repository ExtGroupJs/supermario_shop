from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.gallery import Gallery
from apps.business_app.serializers.gallery import GallerySerializer
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.serializer_map import SerializerMapMixin
from apps.common.pagination import AllResultsSetPagination
from apps.common.permissions import CommonRolePermission


class GalleryViewSet(SerializerMapMixin, viewsets.ModelViewSet, GenericAPIView):
    queryset = Gallery.objects.select_related("product").all()
    serializer_class = GallerySerializer
    permission_classes = [CommonRolePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    pagination_class = AllResultsSetPagination
    filterset_fields = ["product"]
    search_fields = ["product__name"]
    ordering = ["id"]