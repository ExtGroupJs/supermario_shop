from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ClientsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.clients_app"
    verbose_name = _("Clients Application")
