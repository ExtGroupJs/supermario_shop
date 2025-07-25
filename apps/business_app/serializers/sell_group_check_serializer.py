from django.core.exceptions import ValidationError
from rest_framework import serializers


class SellGroupCheckSerializer(serializers.Serializer):
    self_sells = serializers.ListField(child=serializers.CharField(), write_only=True)
    whatsapp_sells = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )

    def validate_self_sells(self, value):
        if not value:
            raise ValidationError("No hay ninguna compra contra la que comparar")
        return value

    def validate_whatsapp_sells(self, value):
        if not value:
            raise ValidationError(
                "No hay ningún listado de compra contra el que comparar"
            )
        return value

    def validate(self, attrs):
        if len(attrs["self_sells"]) != len(attrs["whatsapp_sells"]):
            raise ValidationError("El largo de los dos listados no coincide")
        return attrs
