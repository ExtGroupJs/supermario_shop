from rest_framework import serializers

from apps.business_app.models.pallet import Pallet


class PalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pallet
        fields = "__all__"
