from rest_framework import serializers

from apps.business_app.models.pallet import Pallet


class PalletSerializer(serializers.ModelSerializer):
    pallet_label = serializers.CharField(source="__str__", read_only=True)
    shop_products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Pallet
        fields = (
            "id",
            "shop",
            "pallet_label",
            "shop_products_count",
            "rack",
            "section",
            "number",
        )
