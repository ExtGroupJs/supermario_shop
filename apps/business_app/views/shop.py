from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.views import CommonOrderingFilter

from apps.business_app.models.shop import Shop
from apps.business_app.serializers.shop import ShopSerializer
from apps.common.permissions import CommonRolePermission



class ShopViewSet(viewsets.ModelViewSet, GenericAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [CommonRolePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    search_fields = [
        "name",
        "extra_info",
    ]
