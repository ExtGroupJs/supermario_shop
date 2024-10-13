from rest_framework import serializers

from apps.common.models.generic_log import GenericLog


class GenericLogSerializer(serializers.ModelSerializer):
    model_class = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GenericLog
        fields = [
            "id",
            "created_timestamp",
            "performed_action",
            "content_type",
            "model_class",
            "object_id",
            "details",
            "created_by",
        ]
        read_only_fields = ["id", "created_timestamp", "created_by"]

    def get_model_class(self, object):
        return object.content_type.name
