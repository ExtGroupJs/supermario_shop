# Generated by Django 5.1.1 on 2024-10-10 03:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("users_app", "0003_systemuser_shop"),
    ]

    operations = [
        migrations.CreateModel(
            name="GenericLog",
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
                    "performed_action",
                    models.CharField(
                        choices=[
                            ("C", "creado"),
                            ("U", "modificado"),
                            ("D", "borrado"),
                        ],
                        default="C",
                        max_length=1,
                        verbose_name="Acción",
                    ),
                ),
                ("object_id", models.IntegerField(verbose_name="Object ID")),
                ("details", models.TextField(null=True, verbose_name="Detalles")),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                        verbose_name="Content Type",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="users_app.systemuser",
                        verbose_name="Created By",
                    ),
                ),
            ],
            options={
                "verbose_name": "Log",
                "verbose_name_plural": "Logs",
            },
        ),
    ]
