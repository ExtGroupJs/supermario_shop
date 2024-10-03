from django.db import models

from apps.business_app.models.shop_products import ShopProducts
from apps.common.models import BaseModel


class Sell(BaseModel):
    shop_product = models.ForeignKey(
        to=ShopProducts,
        on_delete=models.DO_NOTHING,
        verbose_name="Producto",
    )
    extra_info = models.TextField(
        verbose_name="Información Extra", null=True, blank=True
    )
    quantity = models.PositiveIntegerField(verbose_name="Cantidad", default=1)
    total_ammount = models.GeneratedField(
        expression=models.F("quantity") * models.F("shop_product__sell_price"),
        output_field=models.DecimalField(max_digits=12, decimal_places=2),
        db_persist=True,
    )
    gain_in_sell = models.GeneratedField(
        expression=models.F("quantity")
        * (models.F("shop_product__sell_price") - models.F("shop_product__cost_price")),
        output_field=models.DecimalField(max_digits=12, decimal_places=2),
        db_persist=False,
    )

    class Meta:
        verbose_name = "Tienda"
        verbose_name_plural = "Tiendas"

    def __str__(self):
        return f"{self.name}"
