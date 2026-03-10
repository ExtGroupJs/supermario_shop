from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("business_app", "0018_rezise_images"),
    ]

    operations = [
        migrations.AddField(
            model_name="shop",
            name="type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("mecanica", "Mecanica"),
                    ("tecnologia", "Tecnologia"),
                    ("alimentos", "Alimentos"),
                    ("otros", "Otros"),
                ],
                default=None,
                max_length=20,
                null=True,
                verbose_name="Tipo",
            ),
        ),
    ]
