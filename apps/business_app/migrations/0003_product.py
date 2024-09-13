# Generated by Django 5.1.1 on 2024-09-13 19:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("business_app", "0002_model"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
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
                    "name",
                    models.CharField(
                        max_length=200, unique=True, verbose_name="Nombre"
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="Descripción"),
                ),
                (
                    "model",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="business_app.model",
                        verbose_name="Modelo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Producto",
                "verbose_name_plural": "Productos",
            },
        ),
    ]
