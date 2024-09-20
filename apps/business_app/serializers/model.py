from rest_framework import serializers
from apps.business_app.models.model import Model
from apps.business_app.serializers.brand import BrandSerializer


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ("id", "name", "brand", "extra_info")


class ReadModelSerializer(ModelSerializer):
    brand = BrandSerializer()

    class Meta(ModelSerializer.Meta):
        model = Model
