from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend

from apps.business_app.models.shop import Shop
from apps.business_app.serializers.shop import ShopSerializer

from apps.common.common_ordering_filter import CommonOrderingFilter

from apps.common.permissions import CommonRolePermission, SellViewSetPermission
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny


class ShopViewSet(viewsets.ModelViewSet, GenericAPIView):
    queryset = Shop.objects.filter(enabled=True)
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

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [SellViewSetPermission]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def catalog(self, request):
        return self.list(request)
