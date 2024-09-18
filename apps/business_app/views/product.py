from rest_framework import filters, permissions, status, viewsets
from rest_framework.generics import GenericAPIView
from apps.business_app.models.product import Product
from apps.business_app.serializers.product import ProductSerializer
from apps.common.views import CommonOrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class ProductViewSet(viewsets.ModelViewSet, GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
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
