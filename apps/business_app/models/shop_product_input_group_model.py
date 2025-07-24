from django.db import models

from apps.business_app.models.shop_products import ShopProducts
from apps.common.models import BaseModel
from django.utils.translation import gettext_lazy as _

from apps.users_app.models.system_user import SystemUser


class ShopProductInputGroup(BaseModel):
    """ """

    for_date = models.DateTimeField(
        verbose_name=_("For date timestamp"), auto_now=True, null=True
    )
    shop_products = models.ManyToManyField(
        ShopProducts, through="ShopProductInput", related_name="input_groups"
    )
    extra_info = models.TextField(
        verbose_name="Información Extra", null=True, blank=True
    )
    author = models.ForeignKey(
        to=SystemUser,
        on_delete=models.DO_NOTHING,
        verbose_name="Autor de la entrada",
        related_name="inputs",
        null=True,
    )

    class Meta:
        verbose_name = "Grupo de Entrada de Productos"
        verbose_name_plural = "Grupos de Entrada de Productos"

    def __str__(self):
        return f"Entrada del día {self.for_date} con {self.shop_products.count()} productos"
