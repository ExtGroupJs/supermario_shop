from django.db import models
from safedelete import SOFT_DELETE_CASCADE

from apps.business_app.models.model import Model
from apps.common.models import BaseModel
from safedelete.models import SafeDeleteModel


class Product(SafeDeleteModel, BaseModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    name = models.CharField(verbose_name="Nombre", max_length=200)
    model = models.ForeignKey(
        to=Model, verbose_name="Modelo", on_delete=models.CASCADE, null=True, blank=True
    )
    description = models.TextField(verbose_name="Descripción", null=True, blank=True)
    image = models.ImageField(verbose_name="Imagen", null=True, blank=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        constraints = [
            # Restricción: Combinación única de 'nombre' y 'categoria'
            models.UniqueConstraint(
                fields=["name", "model"],
                name="name_model_unique",
                violation_error_message="Ya existe un producto con este nombre y para este modelo.",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.model})"
