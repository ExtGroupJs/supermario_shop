from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView
from apps.business_app.models.brand import Brand
from apps.business_app.serializers.brand import BrandSerializer
from django_filters.rest_framework import DjangoFilterBackend

from apps.common.common_ordering_filter import CommonOrderingFilter

from apps.common.permissions import CommonRolePermission


class BrandViewSet(viewsets.ModelViewSet, GenericAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [CommonRolePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]

    search_fields = [
        "name",
    ]
