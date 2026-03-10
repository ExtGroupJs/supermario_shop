from rest_framework import serializers

from apps.business_app.models.shop import Shop


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            "id",
            "name",
            "catalog_url",
            "logo",
            "extra_info",
            "type",
            "enabled",
            "principal",
        ]
