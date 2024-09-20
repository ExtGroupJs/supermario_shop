from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.model import Model
from apps.business_app.serializers.model import ModelSerializer, ReadModelSerializer
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.views import CommonOrderingFilter


class ModelViewSet(viewsets.ModelViewSet, GenericAPIView):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
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

    def get_serializer(self, *args, **kwargs):
        if self.action == "list":
            self.serializer_class = ReadModelSerializer
        return super().get_serializer(*args, **kwargs)
