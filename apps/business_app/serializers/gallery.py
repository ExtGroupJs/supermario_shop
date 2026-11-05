from rest_framework import serializers

from apps.business_app.models.gallery import Gallery


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = (
            "id",
            "product",
            "image",
        )