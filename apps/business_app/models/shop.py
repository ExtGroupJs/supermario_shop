from django.db import models

from apps import business_app

# from apps.business_app.models.product import Product
# from apps.business_app.models.shop_products import ShopProducts


class Shop(models.Model):
    name = models.CharField(verbose_name="Nombre", unique=True, max_length=200)
    logo = models.ImageField(verbose_name="logo")
    extra_info = models.TextField(
        verbose_name="Información Extra", null=True, blank=True
    )
    products = models.ManyToManyField(
        to="apps.business_app.Product", through="apps.business_app.ShopProducts"
    )

    class Meta:
        verbose_name = "Tienda"
        verbose_name_plural = "Tiendas"

    def __str__(self):
        return f"{self.name}"
