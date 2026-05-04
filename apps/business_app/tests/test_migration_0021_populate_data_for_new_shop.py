import importlib

import pytest
from django.apps import apps as django_apps
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from apps.business_app.models.brand import Brand
from apps.business_app.models.model import Model
from apps.business_app.models.product import Product
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts


MIGRATION_MODULE = importlib.import_module(
    "apps.business_app.migrations.0021_populate_data_for_new_shop"
)


def _build_logo_file(filename):
    return SimpleUploadedFile(
        filename, b"fake-image-content", content_type="image/jpeg"
    )


@pytest.mark.django_db
class TestMigration0021PopulateDataForNewShop:
    def test_populate_data_copies_prices_from_source_shop(self):
        """Valida que populate_data copia precios de Tecnología Ciego a Almacén de Tecnología."""
        source_shop = baker.make(
            Shop,
            name="Tecnología Ciego",
            logo=_build_logo_file("source_logo.jpg"),
            type=Shop.TYPE_CHOICES.TECH,
        )
        destiny_shop = baker.make(
            Shop,
            name="Almacén de Tecnología",
            logo=_build_logo_file("destiny_logo.jpg"),
            type=Shop.TYPE_CHOICES.TECH,
        )

        # Crear datos en source_shop para que migrate los copia
        brand1 = baker.make(Brand, name="Apple")
        model1 = baker.make(Model, name="Computadoras-001", brand=brand1)
        product1 = baker.make(Product, name="Asus VivoBook", model=model1)

        baker.make(
            ShopProducts,
            shop=source_shop,
            product=product1,
            quantity=7,
            extra_info="origen",
            cost_price=123.45,
            sell_price=150.75,
            sell_price_for_catalog=160.25,
        )

        # Ejecutar populate_data
        MIGRATION_MODULE.populate_data(django_apps, None)

        # Validar que se creó en destiny_shop con los precios copiados
        created_sp = ShopProducts.objects.get(
            shop=destiny_shop,
            product__name="Asus VivoBook",
        )

        assert created_sp.cost_price == pytest.approx(123.45)
        assert created_sp.sell_price == pytest.approx(150.75)
        assert created_sp.sell_price_for_catalog == pytest.approx(160.25)
        assert created_sp.quantity == 0
        assert created_sp.extra_info == ""

    def test_reverse_populate_data_deletes_only_migration_products(self):
        """Valida que reverse_populate_data elimina solo los productos de la migración."""
        baker.make(
            Shop,
            name="Tecnología Ciego",
            logo=_build_logo_file("source_logo_2.jpg"),
            type=Shop.TYPE_CHOICES.TECH,
        )
        destiny_shop = baker.make(
            Shop,
            name="Almacén de Tecnología",
            logo=_build_logo_file("destiny_logo_2.jpg"),
            type=Shop.TYPE_CHOICES.TECH,
        )

        # Ejecutar populate_data (carga todos los 89 productos de datos_modificados)
        MIGRATION_MODULE.populate_data(django_apps, None)
        count_after_populate = ShopProducts.objects.filter(shop=destiny_shop).count()

        # Crear un producto adicional fuera de la lista de migración
        extra_product = baker.make(Product, name="Producto Fuera Migración")
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

        # Ejecutar reverse_populate_data
        MIGRATION_MODULE.reverse_populate_data(django_apps, None)

        count_after_reverse = ShopProducts.objects.filter(shop=destiny_shop).count()

        # Validar que solo el producto manual quedó
        assert count_after_reverse == 1
        assert ShopProducts.objects.filter(id=extra_sp.id).exists()
        assert not ShopProducts.objects.filter(
            shop=destiny_shop,
            product__name="Asus VivoBook",
        ).exists()
