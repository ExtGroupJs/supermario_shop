import logging

from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.generics import GenericAPIView

from apps.clients_app.models.client import Client
from apps.clients_app.serializers.client import ClientSerializer
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.users_app.serializers.group import GroupSerializer

logger = logging.getLogger(__name__)

# Create your views here.


class ClientViewSet(viewsets.ModelViewSet, GenericAPIView):
    """
    API endpoint that allows clients to be viewed or edited.
    """

    queryset = Client.objects.all()
    serializer_class = ClientSerializer

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
