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
        all_sells = Sell.objects.all()
        for sell in all_sells:
            sell.quantity = 0

        Sell.objects.bulk_update(all_sells, ["quantity"])
        SellGroup.objects.all().delete()
        all_sells.delete()

        GenericLog.objects.all().delete()
        shop_products = ShopProducts.objects.filter(quantity__gt=0)
        
        content_type = ContentType.objects.get_for_model(ShopProducts)
        created_by_id = SystemUser.objects.get(username="dev").id
        logs_to_create = []

        for shop_product in shop_products:
            # Crear el objeto GenericLog sin guardarlo aún
            log = GenericLog(
                performed_action=GenericLog.ACTION.CREATED,
                object_id=shop_product.id,
                content_type=content_type,
                created_by_id = created_by_id,
                details={
                    "quantity": {
                        "old_value": None,
                        "new_value": str(shop_product.quantity),
                    }
                },
            )
            logs_to_create.append(log)
        GenericLog.objects.bulk_create(logs_to_create)

        print(
            colored(
                "Successfully reseted quantities",
                "green",
                attrs=["blink"],
            )
        )
