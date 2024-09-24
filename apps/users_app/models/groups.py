from django.db import models
from django.utils.translation import gettext_lazy as _


class Groups(models.IntegerChoices):
    # ** Administrativo
    SUPER_ADMIN = 1, _("Super Admin")
    SHOP_OWNER = 2, _("Dueño")
    SHOP_SELLER = 3, _("Vendedor")
