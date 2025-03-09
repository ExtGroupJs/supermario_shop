from django.core.management.base import BaseCommand
from termcolor import colored

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop_products import ShopProducts
from apps.common.models.generic_log import GenericLog
from django.contrib.contenttypes.models import ContentType

from apps.users_app.models.system_user import SystemUser


class Command(BaseCommand):
    help = "Loads initial fixtures"

    def handle(self, *args, **options):
        SellGroup.objects.all().delete()
        Sell.objects.all().delete()
        GenericLog.objects.all().delete()
        shop_products = ShopProducts.objects.filter(quantity__gt=0)

        for shop_product in shop_products:
            details = {}
            details["quantity"] = {
                "old_value": None,
                "new_value": shop_product.quantity.__str__(),
            }
            GenericLog.objects.create(
                performed_action=GenericLog.ACTION.CREATED,
                object_id=shop_product.id,
                content_type=ContentType.objects.get_for_model(ShopProducts),
                details=details,
                created_by_id=SystemUser.objects.get(username="dev").id,
            )
        print(
            colored(
                "Successfully reseted quantities",
                "green",
                attrs=["blink"],
            )
        )
