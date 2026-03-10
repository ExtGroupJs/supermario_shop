from django.db import models


class Shop(models.Model):
    WHOLESALE_SHOP_NAME = "Tienda al por mayor"
    TYPE_MECHANIC = "mecanica"
    TYPE_TECHNOLOGY = "tecnologia"
    TYPE_FOOD = "alimentos"
    TYPE_OTHER = "otros"
    TYPE_CHOICES = (
        (TYPE_MECHANIC, "Mecanica"),
        (TYPE_TECHNOLOGY, "Tecnologia"),
        (TYPE_FOOD, "Alimentos"),
        (TYPE_OTHER, "Otros"),
    )

    name = models.CharField(verbose_name="Nombre", unique=True, max_length=200)
    logo = models.ImageField(verbose_name="logo")
    extra_info = models.TextField(
        verbose_name="Información Extra", null=True, blank=True
    )
    type = models.CharField(
        verbose_name="Tipo",
        max_length=20,
        choices=TYPE_CHOICES,
        null=True,
        blank=True,
        default=None,
    )
    products = models.ManyToManyField(
        to="business_app.Product", through="business_app.ShopProducts"
    )
    enabled = models.BooleanField(verbose_name="Habilitado", default=True)

    class Meta:
        verbose_name = "Tienda"
        verbose_name_plural = "Tiendas"

    def __str__(self):
        return f"{self.name}"
