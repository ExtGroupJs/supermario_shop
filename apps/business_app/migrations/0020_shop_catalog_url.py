from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("business_app", "0019_shop_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="shop",
            name="catalog_url",
            field=models.SlugField(
                blank=True,
                max_length=255,
                null=True,
                unique=True,
                verbose_name="URL catálogo",
            ),
        ),
    ]
