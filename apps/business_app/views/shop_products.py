from rest_framework import filters, permissions, status, viewsets
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.shop_products import ShopProductsSerializer
from apps.common.views import CommonOrderingFilter


class ShopProductsViewSet(viewsets.ModelViewSet, GenericAPIView):
    queryset = ShopProducts.objects.all()
    serializer_class = ShopProductsSerializer
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
