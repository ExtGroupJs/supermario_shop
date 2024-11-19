from email.policy import default
from rest_framework import serializers

from apps.business_app.models.sell import Sell
from datetime import datetime

from apps.business_app.models.sell_group import SellGroup


class SellGroupSerializer(serializers.ModelSerializer):
    updated_timestamp = serializers.SerializerMethodField()

    class Meta:
        model = SellGroup
        fields = ("id", "discount", "extra_info", "payment_method", "updated_timestamp")
        read_only_fields = ("id",)

    def get_updated_timestamp(self, object):
        return object.updated_timestamp.strftime("%d-%h-%Y a las  %I:%M %p")
