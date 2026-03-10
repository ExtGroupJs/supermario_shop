from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("business_app", "0020_shop_catalog_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="shop",
            name="principal",
            field=models.BooleanField(default=False, verbose_name="Principal"),
        ),
        migrations.AddConstraint(
            model_name="shop",
            constraint=models.UniqueConstraint(
                condition=Q(("principal", True)),
                fields=("principal",),
                name="unique_principal_shop",
            ),
        ),
    ]
