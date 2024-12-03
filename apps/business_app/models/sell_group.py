from re import S
from django.db import models

from apps.business_app.models.shop_products import ShopProducts
from apps.common.models import BaseModel
from apps.users_app.models.system_user import SystemUser
from django.db.models import F
from django.utils.translation import gettext_lazy as _


class SellGroup(BaseModel):
    """ """

    class PAYMENT_METODS(models.TextChoices):
        USD = "U", _("USD")
        ZELLE = "Z", _("ZELLE")

    discount = models.PositiveSmallIntegerField(verbose_name=_("Descuento"), default=0)
    seller = models.ForeignKey(
        to=SystemUser,
        on_delete=models.DO_NOTHING,
        verbose_name="Vendedor",
        related_name="sell_groups",
        null=True,
    )
    extra_info = models.TextField(
        verbose_name="Información Extra", null=True, blank=True
    )
    payment_method = models.CharField(
        verbose_name=_("Método de Pago"),
        max_length=1,
        choices=PAYMENT_METODS,
        default=PAYMENT_METODS.USD,
    )

    class Meta:
        verbose_name = "Grupo de Venta"
        verbose_name_plural = "Grupos de Ventas"

    # def __str__(self):
    #     return f"{self.shop_product} ({self.shop_product.shop})"
