from rest_framework import serializers

from apps.common.serializers.generic_log import GenericLogSerializer
from apps.users_app.models.system_user import SystemUser
from project_site import settings


class ShopProductsLogsSerializer(GenericLogSerializer):
    shop_product_name = serializers.CharField(read_only=True)
    shop = serializers.IntegerField(read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta(GenericLogSerializer.Meta):
        fields = [
            "created_timestamp",
            "object_id",
            "performed_action",
            "shop_product_name",
            "product_image",
            "shop",
            "created_by",
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        raw_old_value = instance.details.get("quantity").get("old_value")
        old_value = 0 if not raw_old_value else int(raw_old_value)
        new_value = int(instance.details.get("quantity").get("new_value"))
        response["init_value"] = old_value
        response["new_value"] = new_value
        dev_user = SystemUser.objects.filter(username="dev").first()
        created_by_dev_user = dev_user and dev_user.id == instance.created_by_id
        operation = ""
        if created_by_dev_user:
            operation = "+" if new_value > old_value else "-"
            action = "corregido"
        else:
            action = "entrado" if new_value > old_value else "vendido"
        abs_value = abs(new_value - old_value)
        response["info"] = (
            f"{operation}{abs_value} {action}{'s' if abs_value > 1 else ''}"
        )
        return response

    def get_product_image(self, obj):
        # Verifica que el campo de imagen no esté vacío
        if obj.product_image:
            return (
                f"{settings.MEDIA_URL}{obj.product_image}"  # Devuelve la URL completa
            )
        return None
