from django.db import models

from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop_products import ShopProducts
from apps.common.models import BaseModel
from apps.users_app.models.system_user import SystemUser


class Sell(BaseModel):
    """
    A postsave signal is implemented on apps\business_app\signals.py
    """

    sell_group = models.ForeignKey(
        SellGroup,
        verbose_name="Grupo de Ventas",
        related_name="sells",
        on_delete=models.CASCADE,
        null=True,
    )
    shop_product = models.ForeignKey(
        to=ShopProducts,
        on_delete=models.DO_NOTHING,
        verbose_name="Producto",
        related_name="sells",
    )
    seller = models.ForeignKey(
        to=SystemUser,
        on_delete=models.DO_NOTHING,
        verbose_name="Vendedor",
        related_name="sells",
    )
    extra_info = models.TextField(
        verbose_name="Información Extra", null=True, blank=True
    )
    quantity = models.PositiveIntegerField(verbose_name="Cantidad", default=1)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

    def __str__(self):
        return f"{self.shop_product} ({self.shop_product.shop})"
