from django.db import migrations, models


def populate_product_code(apps, schema_editor):
    Product = apps.get_model("business_app", "Product")
    for product in Product.objects.all():
        if product.internal_code:
            continue
        brand = product.model.brand.name if product.model else ""
        model_name = product.model.name if product.model else ""
        brand_code = brand[:2].upper() or "XX"
        model_words = model_name.split()
        if model_words:
            if len(model_words) == 1:
                model_code = model_words[0][:3].upper()
            else:
                model_code = "".join(word[0] for word in model_words[:3]).upper()
        else:
            model_code = "XXX"
        product_words = product.name.split()
        if len(product_words) >= 3:
            product_code = "".join(word[0] for word in product_words[:3]).upper()
        else:
            product_code = product.name[:3].upper()
        product.internal_code = f"{brand_code}{model_code}-{product_code}{product.pk}"
        product.save(update_fields=["internal_code"])


class Migration(migrations.Migration):

    dependencies = [
        ("business_app", "0029_product_unique_product_model_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="internal_code",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=15,
                null=True,
                verbose_name="Código",
            ),
        ),
        migrations.RunPython(
            code=populate_product_code,
            reverse_code=migrations.RunPython.noop,
        ),
    ]