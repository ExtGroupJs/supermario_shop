from django.core import validators
from django.db import migrations, models
from django.db.models import F


def populate_wholesale_price(apps, schema_editor):
    ShopProducts = apps.get_model("business_app", "ShopProducts")
    ShopProducts.objects.filter(wholesale_price__isnull=True).update(
        wholesale_price=F("sell_price")
    )


class Migration(migrations.Migration):
    dependencies = [
        ("business_app", "0026_remove_shopproductinputgroup_shop_products_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="shopproducts",
            name="wholesale_price",
            field=models.FloatField(
                blank=True,
                null=True,
                validators=[validators.MinValueValidator(limit_value=0.3)],
                verbose_name="Precio al por mayor",
            ),
        ),
        migrations.RunPython(
            code=populate_wholesale_price,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="shopproducts",
            name="wholesale_price",
            field=models.FloatField(
                validators=[validators.MinValueValidator(limit_value=0.3)],
                verbose_name="Precio al por mayor",
                blank=True,
                null=True,
            ),
        ),
    ]
