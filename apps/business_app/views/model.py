from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.model import Model
from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.model import ModelSerializer, ReadModelSerializer
from django_filters.rest_framework import DjangoFilterBackend

from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.serializer_map import SerializerMapMixin

from apps.common.permissions import CommonRolePermission, SellViewSetPermission
from django.db.models import F
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

SHOP_FILTER_PARAM = "product__shopproducts__shop"


class ModelViewSet(SerializerMapMixin, viewsets.ModelViewSet, GenericAPIView):
    queryset = Model.objects.all().annotate(brand_name=F("brand__name"))
    serializer_class = ModelSerializer
    list_serializer_class = ReadModelSerializer
    permission_classes = [CommonRolePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    filterset_fields = [
        "brand",
    ]
    search_fields = [
        "name",
        "extra_info",
    ]
    ordering = ["name"]
    ordering_fields = [
        "name",
        "brand_name",
    ]

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [SellViewSetPermission]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "catalog":
            queryset = self._filter_by_shop(queryset)
        return queryset

    def _filter_by_shop(self, queryset):
        """
        Restrict the models to those that have inventory in the shop given by the
        `product__shopproducts__shop` query param.

        A subquery over `ShopProducts` is used instead of the
        `product__shopproducts__shop` ORM join because that join does not honour
        the soft deletes of `Product` and `ShopProducts`, so it would return
        models whose only shop product has been soft deleted.
        """
        shop_id = self.request.query_params.get(SHOP_FILTER_PARAM)
        if not shop_id:
            return queryset
        if not shop_id.isdigit():
            raise ValidationError({SHOP_FILTER_PARAM: "Escoja una tienda válida."})
        models_in_shop = (
            ShopProducts.objects.filter(shop_id=shop_id)
            .filter(product__deleted__isnull=True)
            .values("product__model_id")
        )
        return queryset.filter(id__in=models_in_shop)

    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def catalog(self, request):
        return self.list(request)
