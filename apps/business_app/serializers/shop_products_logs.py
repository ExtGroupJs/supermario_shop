from rest_framework import serializers

from apps.business_app.models.shop_products import ShopProducts
from apps.common.serializers.generic_log import GenericLogSerializer


class ShopProductsLogsSerializer(GenericLogSerializer):
    info = serializers.SerializerMethodField()
    init_value = serializers.SerializerMethodField()
    new_value = serializers.SerializerMethodField()
    shop_product_name = serializers.SerializerMethodField()

    class Meta(GenericLogSerializer.Meta):
        fields = fields = [
            "created_timestamp",
            "info",
            "object_id",
            "performed_action",
            "shop_product_name",
            "init_value",
            "new_value",
            "created_by",
        ]

    def get_info(self, obj):
        quantity = obj.details.get("quantity")
        if isinstance(quantity, dict):
            old_value = int(quantity.get("old_value"))
            new_value = int(quantity.get("new_value"))
        else:
            old_value = 0
            new_value = int(quantity)

        action = "entrado" if new_value > old_value else "vendido"
        abs_value = abs(new_value - old_value)
        return f"{abs_value} {action}{'s' if abs_value>1 else ''}"

    def get_init_value(self, obj):
        quantity = obj.details.get("quantity")
        if isinstance(quantity, dict):
            return quantity.get("old_value")
        return "0"

    def get_new_value(self, obj):
        quantity = obj.details.get("quantity")
        if isinstance(quantity, dict):
            return quantity.get("new_value")
        return quantity

    def get_shop_product_name(self, obj):
        shop_product = ShopProducts.all_objects.get(id=obj.object_id)
        return shop_product.__str__()
