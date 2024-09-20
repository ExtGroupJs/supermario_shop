from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView
from apps.business_app.models.product import Product
from apps.business_app.serializers.product import (
    ProductSerializer,
    ReadProductSerializer,
)
from apps.common.views import CommonOrderingFilter, SerializerMapMixin
from django_filters.rest_framework import DjangoFilterBackend


class ProductViewSet(SerializerMapMixin, viewsets.ModelViewSet, GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    list_serializer_class = ReadProductSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    filterset_fields = [
        "model",
        "model__brand",
    ]
    search_fields = [
        "name",
        "description",
    ]
