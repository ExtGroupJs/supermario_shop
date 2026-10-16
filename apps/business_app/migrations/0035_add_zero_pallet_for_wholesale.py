# Generated manually
from django.db import migrations

WHOLESALE_SHOP_NAME = "Tienda al por mayor"


def create_zero_pallet(apps, schema_editor):
    Pallet = apps.get_model("business_app", "Pallet")
    Shop = apps.get_model("business_app", "Shop")
    shop = Shop.objects.filter(name=WHOLESALE_SHOP_NAME).first()
    if not shop:
        return
    Pallet.objects.get_or_create(
        shop=shop,
        rack=0,
        section="",
        number=0,
        defaults={"shop": shop},
    )


def remove_zero_pallet(apps, schema_editor):
    Pallet = apps.get_model("business_app", "Pallet")
    Shop = apps.get_model("business_app", "Shop")
    shop = Shop.objects.filter(name=WHOLESALE_SHOP_NAME).first()
    if not shop:
        return
    Pallet.objects.filter(shop=shop, rack=0, section="", number=0).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("business_app", "0034_backfill_sellgroup_total_from_sells"),
    ]

    operations = [
        migrations.RunPython(create_zero_pallet, remove_zero_pallet),
    ]
