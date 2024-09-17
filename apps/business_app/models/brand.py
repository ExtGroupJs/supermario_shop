from django.db import models


class Brand(models.Model):
    name = models.CharField(verbose_name="Nombre", unique=True, max_length=25)
    logo = models.ImageField(verbose_name="logo", null=True, blank=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"

    def __str__(self):
        return f"{self.name}"
