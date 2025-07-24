from rest_framework import serializers

from apps.business_app.models.shop_product_input_model import ShopProductInput


class ShopProductInputSerializer(serializers.ModelSerializer):
    # product_name = serializers.CharField(read_only=True)
    created_timestamp = serializers.SerializerMethodField()
    for_date = serializers.SerializerMethodField()

    class Meta:
        model = ShopProductInput
        fields = (
            "id",
            "shop_product",
            "quantity",
            "created_timestamp",
            "for_date",
        )
        read_only_fields = ("id",)

    def get_created_timestamp(self, object):
        return object.created_timestamp.strftime("%d-%h-%Y a las %I:%M %p")

    def get_for_date(self, object):
        return object.shop_product_input_group.for_date.strftime("%d-%h-%Y")
