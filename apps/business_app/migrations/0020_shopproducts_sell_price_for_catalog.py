from django.db import migrations, models
import django.core.validators


def populate_sell_price_for_catalog(apps, schema_editor):
    ShopProducts = apps.get_model("business_app", "ShopProducts")
    ShopProducts.objects.filter(sell_price_for_catalog__isnull=True).update(
        sell_price_for_catalog=models.F("sell_price")
    )


class Migration(migrations.Migration):

    dependencies = [
        ("business_app", "0019_shop_catalog_url_shop_principal_shop_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="shopproducts",
            name="sell_price_for_catalog",
            field=models.FloatField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(limit_value=0.3)],
                verbose_name="Precio de venta para catálogo",
            ),
        ),
        migrations.RunPython(
            populate_sell_price_for_catalog,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
