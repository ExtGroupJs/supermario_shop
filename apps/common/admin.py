# Register your models here.

from django.contrib import admin

from apps.common.models.generic_log import GenericLog


@admin.register(GenericLog)
class GenericLogAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = [
        "id",
        "created_timestamp",
        "performed_action",
        "content_type",
        "object_id",
        "content_object",
        "details",
        "created_by",
    ]
