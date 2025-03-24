from django.contrib import admin


from apps.clients_app.models.client import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = [
        "id",
        "name",
        "phone",
    ]
    fields = [
        "name",
        "phone",
    ]
