from django.db import models

from apps.business_app.models.shop_products import ShopProducts
from apps.common.models.base_model import BaseModel


class ShopProductInput(BaseModel):
    shop_product_input_group = models.ForeignKey(
        "ShopProductInputGroup", on_delete=models.CASCADE, related_name="inputs"
    )
    shop_product = models.ForeignKey(
        ShopProducts, on_delete=models.CASCADE, related_name="shop_product_inputs"
    )
    quantity = models.PositiveIntegerField(verbose_name="Cantidad", default=1)

    class Meta:
        verbose_name = "Entrada de Producto"
        verbose_name_plural = "Entradas de Productos"

    def __str__(self):
        return f"Adicionados {self.quantity} {self.shop_product} en {self.shop_product_input_group}"
