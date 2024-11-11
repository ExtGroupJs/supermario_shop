from rest_framework import serializers

from apps.business_app.models.model import Model
from apps.business_app.serializers.brand import BrandSerializer
from apps.business_app.views import brand


class ModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(read_only=True)

    class Meta:
        model = Model
        fields = (
            "id",
            "name",
            "brand",
            "brand_name",
            "extra_info",
            "__str__",
        )


class ReadModelSerializer(ModelSerializer):
    brand = BrandSerializer()

    class Meta(ModelSerializer.Meta):
        model = Model
