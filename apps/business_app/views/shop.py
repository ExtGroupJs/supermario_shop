from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend

from apps.business_app.models.shop import Shop
from apps.business_app.serializers.shop import ShopSerializer

from apps.common.common_ordering_filter import CommonOrderingFilter

from apps.common.permissions import CommonRolePermission
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers


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

    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
