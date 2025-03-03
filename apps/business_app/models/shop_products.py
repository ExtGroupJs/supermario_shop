from django.db import models
from django.core import validators
from safedelete import SOFT_DELETE

from apps.business_app.models.shop import Shop
from apps.business_app.models.product import Product
from apps.common.mixins.generic_log import GenericLogMixin
from apps.common.models import BaseModel
from django.core.exceptions import ValidationError
from safedelete.models import SafeDeleteModel


class ShopProducts(GenericLogMixin, SafeDeleteModel, BaseModel):
    _safedelete_policy = SOFT_DELETE
    shop = models.ForeignKey(
        to=Shop, on_delete=models.DO_NOTHING, verbose_name="Tienda"
    )
    product = models.ForeignKey(
        to=Product, on_delete=models.DO_NOTHING, verbose_name="Producto"
    )
    extra_info = models.TextField(
        verbose_name="Información Extra", null=True, blank=True
    )
    quantity = models.PositiveIntegerField(verbose_name="Cantidad", default=0)
    cost_price = models.DecimalField(
        verbose_name="Precio de costo",
        decimal_places=2,
        max_digits=8,
        validators=[validators.MinValueValidator(limit_value=0)],
    )
    sell_price = models.DecimalField(
        verbose_name="Precio de venta",
        decimal_places=2,
        max_digits=8,
        validators=[validators.MinValueValidator(limit_value=0)],
    )

    def clean(self):
        super().clean()
        if self.cost_price >= self.sell_price:
            raise ValidationError(
                'El campo "campo_menor" debe ser menor que "campo_mayor".'
            )

    class Meta:
        verbose_name = "Productos en Tienda"
        verbose_name_plural = "Productos en Tiendas"

    def __str__(self):
        return f"{self.product} ({self.shop})"

    def __repr__(self):
        if not self.extra_info:
            return self.product.__str__()
        return f"{self.product} ({self.extra_info})"

    def save(self, *args, **kwargs):
        self.full_clean()  # Valida el modelo antes de guardar
        super().save(*args, **kwargs)

    def investment(self):
        from apps.business_app.models.sell import Sell

        related_sells = Sell.objects.filter(shop_product=self)
        accumulated_selled = 0
        for sell in related_sells:
            accumulated_selled += self.cost_price * sell.quantity
        accumulated_selled += self.cost_price * self.quantity
        return accumulated_selled
