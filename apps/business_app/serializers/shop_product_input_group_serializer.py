from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import serializers


from apps.business_app.models.shop_product_input_group_model import (
    ShopProductInputGroup,
)
from apps.business_app.serializers.shop_product_input_serializer import (
    ShopProductInputSerializer,
)


class ShopProductInputGroupSerializer(serializers.ModelSerializer):
    updated_timestamp = serializers.SerializerMethodField()
    shop_products_input = ShopProductInputSerializer(many=True, write_only=True)

    class Meta:
        model = ShopProductInputGroup
        fields = (
            "id",
            "for_date",
            "updated_timestamp",
            "shop_products",
            "extra_info",
            "author",
            "shop_products_input",
        )
        read_only_fields = ("id",)

    def get_updated_timestamp(self, object):
        return object.updated_timestamp.strftime("%d-%h-%Y a las  %I:%M %p")

    def validate_shop_products_input(self, value: list):
        if len(value) < 1:
            raise ValidationError(
                "El grupo de entrada de productos debe contener al menos un producto"
            )
        return value

    def validate_for_date(self, value):
        if value > timezone.now():
            raise ValidationError(
                "La fecha de la venta no puede ser mayor al momento actual"
            )
        return value
