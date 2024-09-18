from rest_framework import serializers
from apps.business_app.models.model import Model


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = "__all__"
