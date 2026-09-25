import pytest
from django.urls import reverse
from model_bakery import baker

from apps.business_app.models.model import Model
from apps.business_app.models.product import Product
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.business_app.views.model import SHOP_FILTER_PARAM


@pytest.mark.django_db
class TestModelCatalogViewSet(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()
        self.url = reverse("models-catalog")
        self.brand = baker.make("business_app.Brand")
        self.shop = baker.make(Shop, principal=False, enabled=True)
        self.other_shop = baker.make(Shop, principal=False, enabled=True)

    def _make_shop_product(self, model, shop):
        """Create a product of the given model and put it in the given shop."""
        return baker.make(
            ShopProducts,
            shop=shop,
            product=baker.make(Product, model=model),
            quantity=1,
            cost_price=1,
            sell_price=5,
        )

    def test_catalog_returns_only_models_of_the_given_shop(self):
        """Only models with inventory in the requested shop are returned."""
        model_in_shop = baker.make(Model, brand=self.brand, name="Model In Shop")
        model_in_other_shop = baker.make(Model, brand=self.brand, name="Model Other Shop")
        self._make_shop_product(model_in_shop, self.shop)
        self._make_shop_product(model_in_other_shop, self.other_shop)

        response = self.client.get(self.url, {SHOP_FILTER_PARAM: self.shop.id})

        self.assertEqual(response.status_code, 200)
        returned_names = [model["name"] for model in response.data["results"]]
        self.assertEqual(returned_names, ["Model In Shop"])

    def test_catalog_excludes_models_whose_shop_product_is_soft_deleted(self):
        """A soft deleted shop product does not keep its model in the catalog."""
        model_with_deleted_shop_product = baker.make(
            Model, brand=self.brand, name="Model Deleted Shop Product"
        )
        self._make_shop_product(model_with_deleted_shop_product, self.shop).delete()

        response = self.client.get(self.url, {SHOP_FILTER_PARAM: self.shop.id})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            "Model Deleted Shop Product",
            [model["name"] for model in response.data["results"]],
        )

    def test_catalog_excludes_models_whose_product_is_soft_deleted(self):
        """A soft deleted product does not keep its model in the catalog."""
        model_with_deleted_product = baker.make(
            Model, brand=self.brand, name="Model Deleted Product"
        )
        shop_product = self._make_shop_product(model_with_deleted_product, self.shop)
        shop_product.product.delete()

        response = self.client.get(self.url, {SHOP_FILTER_PARAM: self.shop.id})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            "Model Deleted Product",
            [model["name"] for model in response.data["results"]],
        )

    def test_catalog_without_shop_param_returns_every_model(self):
        """The shop filter is optional: without it the catalog is not restricted."""
        baker.make(Model, brand=self.brand, name="Model Without Shop")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Model Without Shop", [model["name"] for model in response.data["results"]]
        )

    def test_catalog_combines_shop_and_brand_filters(self):
        """The brand filter is applied together with the shop filter."""
        wanted_model = baker.make(Model, brand=self.brand, name="Model Wanted")
        other_model = baker.make(
            Model, brand=self.brand, name="Model Not Wanted", brand_id=self.brand.id
        )
        self._make_shop_product(wanted_model, self.shop)
        self._make_shop_product(other_model, self.shop)

        response = self.client.get(
            self.url, {SHOP_FILTER_PARAM: self.shop.id, "brand": self.brand.id}
        )

        self.assertEqual(response.status_code, 200)
        returned_names = [model["name"] for model in response.data["results"]]
        self.assertEqual(sorted(returned_names), ["Model Not Wanted", "Model Wanted"])

    def test_catalog_returns_no_models_for_a_shop_without_inventory(self):
        """A shop without inventory returns an empty catalog."""
        response = self.client.get(self.url, {SHOP_FILTER_PARAM: self.other_shop.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_list_is_not_restricted_by_the_shop_filter(self):
        """The shop filter only applies to the catalog action, not to the list."""
        model_without_shop_product = baker.make(
            Model, brand=self.brand, name="Model Without Shop Product"
        )
        self.client.force_authenticate(self.user)
        self.user.groups.add(1)  # SUPER_ADMIN

        response = self.client.get(
            reverse("models-list"), {SHOP_FILTER_PARAM: self.shop.id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            model_without_shop_product.id,
            [model["id"] for model in response.data["results"]],
        )
