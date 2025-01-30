from os import read
from rest_framework import serializers

from apps.business_app.models.shop_products import ShopProducts
from apps.common.serializers.generic_log import GenericLogSerializer
from project_site import settings


class ShopProductsLogsSerializer(GenericLogSerializer):
    init_value = serializers.SerializerMethodField()
    new_value = serializers.SerializerMethodField()
    shop_product_name = serializers.CharField(read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta(GenericLogSerializer.Meta):
        fields = [
            "created_timestamp",
            "object_id",
            "performed_action",
            "shop_product_name",
            "product_image",
            "created_by",
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        old_value = int(instance.details.get("quantity").get("old_value", 0))
        new_value = int(instance.details.get("quantity").get("new_value"))
        response["init_value"] = old_value
        response["new_value"] = new_value
        action = "entrado" if new_value > old_value else "vendido"
        abs_value = abs(new_value - old_value)
        response["info"] = f"{abs_value} {action}{'s' if abs_value>1 else ''}"
        return response

    def get_product_image(self, obj):
        # Verifica que el campo de imagen no esté vacío
        if obj.product_image:
            return (
                f"{settings.MEDIA_URL}{obj.product_image}"  # Devuelve la URL completa
            )
        return None
