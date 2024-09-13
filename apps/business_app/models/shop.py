from django.db import models


class Shop(models.Model):
    name = models.CharField(verbose_name="Nombre", unique=True, max_length=200)
    logo = models.ImageField(verbose_name="logo")
    extra_info = models.TextField(
        verbose_name="Información Extra", null=True, blank=True
    )

    class Meta:
        verbose_name = "Tienda"
        verbose_name_plural = "Tiendas"

    def __str__(self):
        return f"{self.name}"
