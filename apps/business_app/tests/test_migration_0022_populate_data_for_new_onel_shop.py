import importlib

import pytest
from django.apps import apps as django_apps
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from apps.business_app.models.product import Product
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts


MIGRATION_MODULE = importlib.import_module(
    "apps.business_app.migrations.0022_populate_data_for_new_onel_shop"
)


def _build_logo_file(filename):
    return SimpleUploadedFile(
        filename, b"fake-image-content", content_type="image/jpeg"
    )


def _get_or_create_shop(name, logo_filename):
    existing_shop = Shop.objects.filter(name=name).first()
    if existing_shop:
        return existing_shop

    return baker.make(
        Shop,
        name=name,
        logo=_build_logo_file(logo_filename),
        type=Shop.TYPE_CHOICES.TECH,
    )


@pytest.mark.django_db
class TestMigration0022PopulateDataForNewOnelShop:
    def test_populate_data_copies_prices_from_source_shop(self):
        """Valida que populate_data copia precios de Tecnología Ciego a Tecnología Ciego (Onel)."""
        source_shop = _get_or_create_shop("Tecnología Ciego", "source_logo.jpg")
        destiny_shop = _get_or_create_shop(
            "Tecnología Ciego (Onel)", "destiny_logo.jpg"
        )

        source_product = baker.make(Product, name="Asus VivoBook")
        baker.make(
            ShopProducts,
            shop=source_shop,
            product=source_product,
            quantity=4,
            extra_info="origen",
            cost_price=210.15,
            sell_price=280.40,
            sell_price_for_catalog=300.50,
        )

        MIGRATION_MODULE.populate_data(django_apps, None)

        created_sp = ShopProducts.objects.get(
            shop=destiny_shop,
            product__name="Asus VivoBook",
        )

        assert created_sp.cost_price == pytest.approx(210.15)
        assert created_sp.sell_price == pytest.approx(280.40)
        assert created_sp.sell_price_for_catalog == pytest.approx(300.50)
        assert created_sp.quantity == 0
        assert created_sp.extra_info == ""

    def test_reverse_populate_data_deletes_only_migration_products(self):
        """Valida que reverse_populate_data elimina solo los productos creados por la migración."""
        _get_or_create_shop("Tecnología Ciego", "source_logo_2.jpg")
        destiny_shop = _get_or_create_shop(
            "Tecnología Ciego (Onel)", "destiny_logo_2.jpg"
        )

        MIGRATION_MODULE.populate_data(django_apps, None)
        count_after_populate = ShopProducts.objects.filter(shop=destiny_shop).count()

        extra_product = baker.make(Product, name="Producto Fuera Migracion")
        extra_sp = baker.make(
            ShopProducts,
            shop=destiny_shop,
            product=extra_product,
            quantity=2,
            extra_info="manual",
            cost_price=10.0,
            sell_price=20.0,
        )

        count_before_reverse = ShopProducts.objects.filter(shop=destiny_shop).count()
        assert count_before_reverse == count_after_populate + 1

        MIGRATION_MODULE.reverse_populate_data(django_apps, None)

        count_after_reverse = ShopProducts.objects.filter(shop=destiny_shop).count()

        assert count_after_reverse == 1
        assert ShopProducts.objects.filter(id=extra_sp.id).exists()
        assert not ShopProducts.objects.filter(
            shop=destiny_shop,
            product__name="Asus VivoBook",
        ).exists()
