from rest_framework import serializers

from apps.clients_app.models.client import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "name", "phone", "shop"]
