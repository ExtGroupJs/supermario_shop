from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.model import Model
from apps.business_app.serializers.model import ModelSerializer, ReadModelSerializer
from django_filters.rest_framework import DjangoFilterBackend

from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.serializer_map import SerializerMapMixin

from apps.common.permissions import CommonRolePermission
from django.db.models import F
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny


class ModelViewSet(SerializerMapMixin, viewsets.ModelViewSet, GenericAPIView):
    queryset = Model.objects.all().annotate(brand_name=F("brand__name"))
    serializer_class = ModelSerializer
    list_serializer_class = ReadModelSerializer
    permission_classes = [CommonRolePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    filterset_fields = [
        "brand",
    ]
    search_fields = [
        "name",
        "extra_info",
    ]
    ordering = ["name"]
    ordering_fields = [
        "name",
        "brand_name",
    ]

    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def catalog(self, request):
        return self.list(request)
