from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.product import Product
from apps.business_app.serializers.product import (
    ProductSerializer,
    ReadProductSerializer,
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.serializer_map import SerializerMapMixin
from apps.common.pagination import AllResultsSetPagination

from apps.common.permissions import CommonRolePermission
from django.db.models import Q, QuerySet, Value, F
from django.db.models.functions import Concat

class ProductViewSet(SerializerMapMixin, viewsets.ModelViewSet, GenericAPIView):
    queryset = Product.objects.all().annotate(
        model_name=Concat(F("model__brand__name"), Value(" - "), F("model__name"))
    )
    serializer_class = ProductSerializer
    list_serializer_class = ReadProductSerializer
    permission_classes = [CommonRolePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    pagination_class = AllResultsSetPagination
    filterset_fields = [
        "model",
        "model__brand",
    ]
    search_fields = [
        "name",
        "description",
    ]
    ordering = ["name"]
    ordering_fields = ["name", "model_name", "description"]


    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
