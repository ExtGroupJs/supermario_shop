from django.db import models
from django.utils.translation import gettext_lazy as _


class AllowedFrequencies(models.TextChoices):
    DAY = "day", _("Día")
    WEEK = "week", _("Semana")
    MONTH = "month", _("Mes")
    QUARTER = "quarter", _("Trimestre")
    YEAR = "year", _("Año")
