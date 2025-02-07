from rest_framework import serializers

from apps.business_app.serializers.model import ModelSerializer
from apps.clients_app.models.client import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "name", "phone", "shop", "models"]


class ClientReadSerializer(ClientSerializer):
    models = ModelSerializer(many=True)

    class Meta(ClientSerializer.Meta):
        fields = ["id", "name", "phone", "shop", "models"]
