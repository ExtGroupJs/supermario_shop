from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView
from apps.business_app.models.brand import Brand
from apps.business_app.serializers.brand import BrandSerializer
from django_filters.rest_framework import DjangoFilterBackend

from apps.common import permissions
from apps.common.common_ordering_filter import CommonOrderingFilter
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from apps.common.permissions import CommonRolePermission
from rest_framework.permissions import AllowAny
from project_site import settings
from rest_framework.decorators import action


class BrandViewSet(viewsets.ModelViewSet, GenericAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [CommonRolePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]

    search_fields = [
        "name",
    ]

    @method_decorator(cache_page(settings.CACHE_DEFAULT_TIMEOUT))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def catalog(self, request):
        return self.list(request)
