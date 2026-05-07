from django.db.models import F, Value
from django.db.models.functions import Concat
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins
from rest_framework.viewsets import GenericViewSet

from apps.business_app.models.input import Input
from apps.business_app.serializers.input import InputSerializer
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.permissions import InputGroupViewSetPermission
from apps.users_app.models.groups import Groups
from apps.users_app.models.system_user import SystemUser


class InputViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Input.objects.all().select_related(
        "shop_product", "author", "input_group"
    )
    serializer_class = InputSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    permission_classes = [InputGroupViewSetPermission]
    filterset_fields = {
        "shop_product": ["exact"],
        "shop_product__shop": ["exact"],
        "author": ["exact"],
        "shop_product__product": ["exact"],
        "shop_product__product__model": ["exact"],
        "shop_product__product__model__brand": ["exact"],
        "quantity": ["gte", "lte", "exact"],
        "created_timestamp": ["gte", "lte"],
        "updated_timestamp": ["gte", "lte"],
    }

    search_fields = [
        "shop_product__product__name",
        "shop_product__product__model__name",
        "shop_product__product__model__brand__name",
        "author__username",
        "input_group__extra_info",
    ]

    ordering_fields = InputSerializer.Meta.fields

    def perform_create(self, serializer):
        serializer.save(author=SystemUser.objects.get(id=self.request.user.id))

    def get_queryset(self):
        queryset = super().get_queryset()
        request_user = self.request.user if not self.request.user.is_anonymous else None

        product_name = Concat(
            F("shop_product__product__name"),
            Value(" ("),
            F("shop_product__product__model__brand__name"),
            Value(" - "),
            F("shop_product__product__model__name"),
            Value(") "),
        )
        if request_user.groups.filter(
            id__in=[Groups.SHOP_OWNER.value, Groups.SUPER_ADMIN.value]
        ).exists():
            queryset = queryset.annotate(
                product_name=Concat(
                    product_name,
                    Value(" - "),
                    F("shop_product__shop__name"),
                )
            )
        else:
            queryset = queryset.filter(
                shop_product__shop=SystemUser.objects.get(id=request_user.id).shop
            ).annotate(product_name=product_name)
        return queryset
