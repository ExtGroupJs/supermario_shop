# Generated by Django 5.1.1 on 2024-09-17 19:05

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("business_app", "0004_shop"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShopProducts",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_timestamp",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created timestamp"
                    ),
                ),
                (
                    "updated_timestamp",
                    models.DateTimeField(
                        auto_now=True, null=True, verbose_name="Updated timestamp"
                    ),
                ),
                (
                    "extra_info",
                    models.TextField(
                        blank=True, null=True, verbose_name="Información Extra"
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(default=0, verbose_name="Cantidad"),
                ),
                (
                    "cost_price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=8,
                        validators=[
                            django.core.validators.MinValueValidator(limit_value=0)
                        ],
                        verbose_name="Precio de costo",
                    ),
                ),
                (
                    "sell_price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=8,
                        validators=[
                            django.core.validators.MinValueValidator(limit_value=0)
                        ],
                        verbose_name="Precio de venta",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="business_app.product",
                        verbose_name="Producto",
                    ),
                ),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="business_app.shop",
                        verbose_name="Tienda",
                    ),
                ),
            ],
            options={
                "verbose_name": "Productos en Tienda",
                "verbose_name_plural": "Productos en Tiendas",
            },
        ),
        migrations.AddField(
            model_name="shop",
            name="products",
            field=models.ManyToManyField(
                through="business_app.ShopProducts", to="business_app.product"
            ),
        ),
    ]