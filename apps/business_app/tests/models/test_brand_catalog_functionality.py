import pytest
from django.urls import reverse
from model_bakery import baker

from apps.business_app.models.brand import Brand
from apps.business_app.models.model import Model
from apps.business_app.models.product import Product
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.business_app.views.brand import SHOP_FILTER_PARAM


@pytest.mark.django_db
class TestBrandCatalogViewSet(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()
        self.url = reverse("brands-catalog")

    def _clear_shops(self):
        """The test DB ships with fixture shops, so each test starts clean.

        `ShopProducts.shop` is `on_delete=DO_NOTHING`, so the join table must be
        emptied by hand to avoid dangling foreign keys.
        """
        ShopProducts.objects.all()._raw_delete(ShopProducts.objects.db)
        Shop.objects.all().delete()

    def _seed_shop_brand(self, *, principal, enabled, name, quantity=5):
        """Create an enabled shop owning a brand through its model/product."""
        shop = baker.make(Shop, principal=principal, enabled=enabled, name=name)
        brand = baker.make(Brand, name=f"brand-{name}")
        model = baker.make(Model, brand=brand, name=f"model-{name}")
        product = baker.make(Product, model=model, name=f"product-{name}")
        baker.make(
            ShopProducts,
            shop=shop,
            product=product,
            quantity=quantity,
            sell_price=10,
            wholesale_price=10,
        )
        return shop, brand

    def _ids(self, response):
        return {brand["id"] for brand in response.data["results"]}

    def test_catalog_without_shop_param_uses_principal_shop(self):
        self._clear_shops()
        _, principal_brand = self._seed_shop_brand(
            principal=True, enabled=True, name="Principal"
        )
        self._seed_shop_brand(principal=False, enabled=True, name="Other")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._ids(response), {principal_brand.id})

    def test_catalog_without_principal_shop_falls_back_to_first_enabled(self):
        self._clear_shops()
        _, first_brand = self._seed_shop_brand(
            principal=False, enabled=True, name="First"
        )
        self._seed_shop_brand(principal=False, enabled=True, name="Second")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._ids(response), {first_brand.id})

    def test_catalog_without_any_shop_returns_empty(self):
        self._clear_shops()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_catalog_ignores_disabled_principal_shop(self):
        self._clear_shops()
        self._seed_shop_brand(principal=True, enabled=False, name="DisabledPrincipal")
        _, enabled_brand = self._seed_shop_brand(
            principal=False, enabled=True, name="Enabled"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._ids(response), {enabled_brand.id})

    def test_catalog_with_shop_param_ignores_the_principal_shop(self):
        self._clear_shops()
        self._seed_shop_brand(principal=True, enabled=True, name="Principal")
        other_shop, other_brand = self._seed_shop_brand(
            principal=False, enabled=True, name="Other"
        )

        response = self.client.get(self.url, {SHOP_FILTER_PARAM: other_shop.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._ids(response), {other_brand.id})

    def test_catalog_with_invalid_shop_param_returns_400(self):
        self._clear_shops()
        self._seed_shop_brand(principal=True, enabled=True, name="Principal")

        response = self.client.get(self.url, {SHOP_FILTER_PARAM: "abc"})

        self.assertEqual(response.status_code, 400)
        self.assertIn(SHOP_FILTER_PARAM, response.data)

    def test_catalog_excludes_brand_whose_only_product_is_out_of_stock(self):
        self._clear_shops()
        self._seed_shop_brand(principal=True, enabled=True, name="Principal")
        self._seed_shop_brand(
            principal=False, enabled=True, name="SoldOut", quantity=0
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            [brand["name"] for brand in response.data["results"]],
            ["brand-Principal"],
        )

    def test_catalog_keeps_brand_with_stock_in_another_product(self):
        """A brand stays in the catalog while any of its products has stock."""
        self._clear_shops()
        shop = baker.make(Shop, principal=True, enabled=True, name="Principal")
        brand = baker.make(Brand, name="brand-Mixed")
        model = baker.make(Model, brand=brand, name="model-Mixed")
        baker.make(
            ShopProducts,
            shop=shop,
            product=baker.make(Product, model=model, name="product-SoldOut"),
            quantity=0,
            sell_price=10,
            wholesale_price=10,
        )
        baker.make(
            ShopProducts,
            shop=shop,
            product=baker.make(Product, model=model, name="product-InStock"),
            quantity=3,
            sell_price=10,
            wholesale_price=10,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self._ids(response), {brand.id})

    def test_catalog_excludes_brand_whose_product_is_soft_deleted(self):
        self._clear_shops()
        shop, _ = self._seed_shop_brand(
            principal=True, enabled=True, name="Deleted"
        )
        ShopProducts.objects.filter(shop=shop).first().product.delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.data["count"], 0)

    def test_list_action_is_not_restricted_to_a_shop(self):
        """The catalog fallback only applies to the catalog action."""
        self.client.force_authenticate(self.user)
        self.user.is_superuser = True
        self.user.save()
        self._clear_shops()
        self._seed_shop_brand(principal=True, enabled=True, name="Principal")
        orphan_brand = baker.make(Brand, name="Orphan")

        response = self.client.get(reverse("brands-list"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn(orphan_brand.id, self._ids(response))
