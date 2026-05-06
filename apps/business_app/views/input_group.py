from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


from apps.business_app.models.input_group import (
    InputGroup,
)
from apps.business_app.models.input import Input

from apps.business_app.serializers.input_group import (
    InputGroupSerializer,
    ReadInputGroupSerializer,
)
from apps.common.common_ordering_filter import CommonOrderingFilter

from apps.common.permissions import (
    InputGroupViewSetPermission,
)
from apps.users_app.models.system_user import SystemUser
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status


class InputGroupViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = InputGroup.objects.all()
    serializer_class = InputGroupSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        CommonOrderingFilter,
    ]
    permission_classes = [InputGroupViewSetPermission]

    filterset_fields = {
        # "shop_product__sell_price": ["gte", "lte", "exact"],
    }

    search_fields = [
        # "shop_product__product__name",
        # "extra_info",
    ]

    ordering_fields = InputGroupSerializer.Meta.fields

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ReadInputGroupSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shop_products_input = serializer.validated_data.pop("shop_products_input")
        created_shop_product_input_group = self.perform_create(serializer)
        for input_data in shop_products_input:
            if "shop_product" in input_data:
                input_data["shop_product_id"] = input_data.pop("shop_product")
            input_data["input_group"] = created_shop_product_input_group
            input_data["author"] = created_shop_product_input_group.author
            Input.objects.create(**input_data)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        return serializer.save(author=SystemUser.objects.get(id=self.request.user.id))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        for input in instance.inputs.all():
            input.delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
