from rest_framework import filters, permissions, status, viewsets
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.views import CommonOrderingFilter

from apps.business_app.models.shop import Shop
from apps.business_app.serializers.shop import ShopSerializer


class ShopViewSet(viewsets.ModelViewSet, GenericAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
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
