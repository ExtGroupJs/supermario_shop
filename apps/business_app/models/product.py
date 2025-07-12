from django.db import models
from safedelete import SOFT_DELETE_CASCADE

from apps.business_app.models.model import Model
from apps.common.models import BaseModel
from safedelete.models import SafeDeleteModel
from PIL import Image



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

    def __str__(self):
        return f"{self.name} ({self.model})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Abrir imagen
        if self.image:
            img = Image.open(self.image.path)

            # Redimensionar manteniendo proporción
            resized_image = img.resize(size=(768, 768), reducing_gap=3.0)

            # Guardar imagen redimensionada
            resized_image.save(self.image.path)

