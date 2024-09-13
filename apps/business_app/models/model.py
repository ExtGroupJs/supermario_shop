from django.db import models

from apps.business_app.models.brand import Brand


class Model(models.Model):
    name = models.CharField(verbose_name="Nombre", unique=True, max_length=250)
    brand = models.ForeignKey(to=Brand, verbose_name="Marca", on_delete=models.CASCADE)
    extra_info = models.TextField(
        verbose_name="Información Extra", null=True, blank=True
    )

    class Meta:
        verbose_name = "Modelos"
        verbose_name_plural = "Modelos"

    def __str__(self):
        return f"{self.name}"
