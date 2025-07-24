from rest_framework import serializers

from apps.common.serializers.generic_log import GenericLogSerializer
from apps.users_app.models.system_user import SystemUser
from project_site import settings


class ShopProductsLogsSerializer(GenericLogSerializer):
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
        quantity = instance.details.get("quantity", {})
        old_value = int(quantity.get("old_value") or 0)
        new_value = int(quantity.get("new_value") or 0)
        response["init_value"] = old_value
        response["new_value"] = new_value

        diff = new_value - old_value
        operation = ""
        action = instance.extra_log_info or ("entrado" if diff > 0 else "vendido")

        dev_user_id = getattr(
            SystemUser.objects.filter(username="dev").only("id").first(), "id", None
        )
        created_by_dev_user = dev_user_id == instance.created_by_id

        if created_by_dev_user:
            if diff < 0:
                operation = "-"
            else:
                operation = "+"
            action = instance.extra_log_info or "actualizado"


        abs_diff = abs(diff)
        suffix = "" if instance.extra_log_info else ("s" if abs_diff > 1 else "")
        response["info"] = f"{operation}{abs_diff} {action}{suffix}"
        return response

    def get_product_image(self, obj):
        # Verifica que el campo de imagen no esté vacío
        if obj.product_image:
            return (
                f"{settings.MEDIA_URL}{obj.product_image}"  # Devuelve la URL completa
            )
        return None
