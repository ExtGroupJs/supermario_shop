from rest_framework import serializers

from apps.common.serializers.generic_log import GenericLogSerializer


class ShopProductsLogsSerializer(GenericLogSerializer):
    info = serializers.SerializerMethodField()
    init_value = serializers.SerializerMethodField()
    new_value = serializers.SerializerMethodField()

    class Meta(GenericLogSerializer.Meta):
        fields = fields = [
            "created_timestamp",
            "info",
            "init_value",
            "new_value",
            "created_by",
        ]

    def get_info(self, obj):
        old_value = int(obj.details.get("quantity").get("old_value"))
        new_value = int(obj.details.get("quantity").get("new_value"))

        action = "entrado" if new_value > old_value else "vendido"
        abs_value = abs(new_value - old_value)
        return f"{abs_value} {action}{'s' if abs_value>1 else ''}"

    def get_init_value(self, obj):
        return obj.details.get("quantity").get("old_value")

    def get_new_value(self, obj):
        return obj.details.get("quantity").get("new_value")
