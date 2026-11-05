from django.db import models

from apps.business_app.models.product import Product


class Gallery(models.Model):
    product = models.ForeignKey(
        to=Product,
        verbose_name="Producto",
        on_delete=models.CASCADE,
        related_name="gallery",
    )
    image = models.ImageField(verbose_name="Imagen", null=True, blank=True)

    class Meta:
        verbose_name = "Galería"
        verbose_name_plural = "Galerías"

    def __str__(self):
        return f"{self.product} - {self.image}"