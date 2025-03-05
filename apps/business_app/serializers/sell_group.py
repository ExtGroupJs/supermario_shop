from django.core.exceptions import ValidationError
from rest_framework import serializers


from apps.business_app.models.sell_group import SellGroup
from apps.business_app.serializers.sell import SellSerializer


class SellGroupSerializer(serializers.ModelSerializer):
    updated_timestamp = serializers.SerializerMethodField()
    sells = SellSerializer(many=True)

    class Meta:
        model = SellGroup
        fields = (
            "id",
            "discount",
            "extra_info",
            "payment_method",
            "seller",
            "updated_timestamp",
            "sells",
            "client",
        )
        read_only_fields = ("id",)

    def get_updated_timestamp(self, object):
        return object.updated_timestamp.strftime("%d-%h-%Y a las  %I:%M %p")

    def validate_sells(self, value: list):
        if len(value) < 1:
            raise ValidationError("La venta debe contener al menos un elemento")
        return value
