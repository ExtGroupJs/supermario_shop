from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.model import Model
from apps.business_app.serializers.model import ModelSerializer, ReadModelSerializer
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.views import CommonOrderingFilter, SerializerMapMixin


class ModelViewSet(SerializerMapMixin, viewsets.ModelViewSet, GenericAPIView):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    list_serializer_class = ReadModelSerializer
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
