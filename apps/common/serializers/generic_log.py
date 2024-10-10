from rest_framework import serializers

from apps.common.models.generic_log import GenericLog


class GenericLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericLog
        fields = [
            "id",
            "created_timestamp",
            "performed_action",
            "content_type",
            "object_id",
            "content_object",
            "details",
            "created_by",
        ]
        read_only_fields = ["id", "created_timestamp", "created_by"]
