from rest_framework import filters, permissions, status, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.model import Model
from apps.business_app.serializers.model import ModelSerializer
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
        "username",
    ]
    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
    ]
