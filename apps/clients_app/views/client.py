import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.generics import GenericAPIView

from apps.clients_app.models.client import Client
from apps.clients_app.serializers.client import ClientReadSerializer, ClientSerializer
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.serializer_map import SerializerMapMixin

logger = logging.getLogger(__name__)

# Create your views here.


class ClientViewSet(SerializerMapMixin, viewsets.ModelViewSet, GenericAPIView):
    """
    API endpoint that allows clients to be viewed or edited.
    """

    queryset = Client.objects.all().prefetch_related("models")
    serializer_class = ClientSerializer
    list_serializer_class = ClientReadSerializer
    retrieve_serializer_class = ClientReadSerializer

    search_fields = [
        "name",
        "phone",
    ]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    ordering = ["name"]

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["shop"]
