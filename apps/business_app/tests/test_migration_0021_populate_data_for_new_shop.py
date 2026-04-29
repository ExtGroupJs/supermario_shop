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
    return SimpleUploadedFile(filename, b"fake-image-content", content_type="image/jpeg")


@pytest.mark.django_db
class TestMigration0021PopulateDataForNewShop:
    def test_populate_data_creates_shop_products_and_copies_prices_from_source_shop(self):
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

        brand = baker.make(Brand, name="Portatil")
        model = baker.make(Model, name="Computadoras", brand=brand)
        product = baker.make(Product, name="Asus VivoBook", model=model)

        baker.make(
            ShopProducts,
            shop=source_shop,
            product=product,
            quantity=7,
            extra_info="origen",
            cost_price=123.45,
            sell_price=150.75,
            sell_price_for_catalog=160.25,
        )

        second_brand = baker.make(Brand, name="Xiaomi")
        second_model = baker.make(Model, name="Teléfonos", brand=second_brand)
        second_product = baker.make(Product, name="Redmi 15C", model=second_model)
        baker.make(
            ShopProducts,
            shop=source_shop,
            product=second_product,
            quantity=4,
            extra_info="origen-dos",
            cost_price=77.2,
            sell_price=99.5,
            sell_price_for_catalog=110.0,
        )

        MIGRATION_MODULE.populate_data(django_apps, None)

        created_first_shop_product = ShopProducts.objects.get(
            shop=destiny_shop,
            product__name="Asus VivoBook",
        )
        created_second_shop_product = ShopProducts.objects.get(
            shop=destiny_shop,
            product__name="Redmi 15C",
        )

        assert created_first_shop_product.cost_price == pytest.approx(123.45)
        assert created_first_shop_product.sell_price == pytest.approx(150.75)
        assert created_first_shop_product.sell_price_for_catalog == pytest.approx(160.25)
        assert created_first_shop_product.quantity == 0
        assert created_first_shop_product.extra_info == ""

        assert created_second_shop_product.cost_price == pytest.approx(77.2)
        assert created_second_shop_product.sell_price == pytest.approx(99.5)
        assert created_second_shop_product.sell_price_for_catalog == pytest.approx(110.0)
        assert created_second_shop_product.quantity == 0
        assert created_second_shop_product.extra_info == ""

    def test_reverse_populate_data_deletes_only_migration_shop_products(self):
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

        MIGRATION_MODULE.populate_data(django_apps, None)

        extra_product = baker.make(Product, name="Producto fuera de lista")
        extra_shop_product = baker.make(
            ShopProducts,
            shop=destiny_shop,
            product=extra_product,
            quantity=2,
            extra_info="manual",
            cost_price=1.0,
            sell_price=2.0,
            sell_price_for_catalog=2.5,
        )

        assert ShopProducts.objects.filter(
            shop=destiny_shop,
            product__name="Asus VivoBook",
        ).exists()

        count_before_reverse = ShopProducts.objects.filter(shop=destiny_shop).count()
        assert count_before_reverse > 1

        MIGRATION_MODULE.reverse_populate_data(django_apps, None)

        count_after_reverse = ShopProducts.objects.filter(shop=destiny_shop).count()

        assert not ShopProducts.objects.filter(
            shop=destiny_shop,
            product__name="Asus VivoBook",
        ).exists()
        assert ShopProducts.objects.filter(id=extra_shop_product.id).exists()
        assert count_after_reverse == 1
