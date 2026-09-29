import pytest
from django.urls import reverse
from model_bakery import baker

from apps.business_app.models.product import Product
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass


@pytest.mark.django_db
class TestShopProductsCatalogStockFilter(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()
        self.url = reverse("shop-products-catalog")

    def _clear_shops(self):
        """The test DB ships with fixture shops, so each test starts clean.

        `SystemUser.shop` is a CASCADE FK, so the test user is detached first to
        keep the delete from taking it down.
        """
        ShopProducts.objects.all()._raw_delete(ShopProducts.objects.db)
        if self.user.shop_id:
            self.user.shop = None
            self.user.save(update_fields=["shop"])
        Shop.objects.all().delete()

    def _make_admin(self):
        """The stock bypass keys off the SUPER_ADMIN group, not is_superuser."""
        self.client.force_authenticate(self.user)
        self.user.is_superuser = True
        self.user.groups.add(1)  # SUPER_ADMIN
        self.user.save()

    def _make_shop_product(self, shop, *, quantity, name="product"):
        return baker.make(
            ShopProducts,
            shop=shop,
            product=baker.make(Product, name=name),
            quantity=quantity,
            cost_price=1,
            sell_price=5,
        )

    def _ids(self, response):
        return {item["id"] for item in response.data["results"]}

    def test_catalog_hides_out_of_stock_rows(self):
        self._clear_shops()
        shop = baker.make(Shop, principal=True, enabled=True, name="Principal")
        in_stock = self._make_shop_product(shop, quantity=3, name="InStock")
        self._make_shop_product(shop, quantity=0, name="SoldOut")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self._ids(response), {in_stock.id})

    def test_catalog_hides_out_of_stock_rows_even_for_admins(self):
        """Admins bypass the stock filter on management endpoints, but the
        public catalog must never publish sold out items."""
        self._make_admin()
        self._clear_shops()
        shop = baker.make(Shop, principal=True, enabled=True, name="Principal")
        in_stock = self._make_shop_product(shop, quantity=3, name="InStock")
        self._make_shop_product(shop, quantity=0, name="SoldOut")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self._ids(response), {in_stock.id})

    def test_catalog_excludes_soft_deleted_shop_product(self):
        self._clear_shops()
        shop = baker.make(Shop, principal=True, enabled=True, name="Principal")
        deleted = self._make_shop_product(shop, quantity=3, name="Deleted")
        deleted.delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.data["results"], [])

    def test_list_keeps_out_of_stock_rows_for_admins(self):
        """The stock filter stays role dependent outside the catalog."""
        self._make_admin()
        self._clear_shops()
        shop = baker.make(Shop, principal=True, enabled=True, name="Principal")
        sold_out = self._make_shop_product(shop, quantity=0, name="SoldOut")

        response = self.client.get(reverse("shop-products-list"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn(sold_out.id, self._ids(response))
