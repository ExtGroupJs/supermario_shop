from django.db import models


class Pallet(models.Model):
    rack = models.PositiveSmallIntegerField(verbose_name="Rack")
    section = models.CharField(verbose_name="Sección", max_length=1)
    number = models.PositiveSmallIntegerField(verbose_name="Número")

    class Meta:
        verbose_name = "Pallet"
        verbose_name_plural = "Pallets"
        constraints = [
            models.UniqueConstraint(
                fields=["rack", "section", "number"],
                name="unique_pallet_rack_section_number",
            )
        ]

    def __str__(self):
        return f"{self.rack}{self.section}{self.number}"
