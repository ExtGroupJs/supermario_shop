from django.db import models

from apps.business_app.models.model import Model
from apps.common.models import BaseModel


class Product(BaseModel):
    name = models.CharField(verbose_name="Nombre", unique=True, max_length=200)
    model = models.ForeignKey(
        to=Model, verbose_name="Modelo", on_delete=models.CASCADE, null=True, blank=True
    )
    description = models.TextField(verbose_name="Descripción", null=True, blank=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.name} ({self.model})"
