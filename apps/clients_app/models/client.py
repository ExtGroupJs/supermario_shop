import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.business_app.models.shop import Shop
from django.core.validators import RegexValidator


class Client(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre completo")

    phone = models.CharField(
        verbose_name=_("phone number"),
        max_length=30,
        null=True,
        blank=True,
        validators=[
            RegexValidator(regex=r"^\+?\d+$", message="Only numeric characters allowed")
        ],
    )
    shop = models.ForeignKey(to=Shop, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")

    def __str__(self):
        return f"{self.name} ({self.shop})"
