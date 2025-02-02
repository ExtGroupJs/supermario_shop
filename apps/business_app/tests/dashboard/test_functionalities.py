import pytest
from django.urls import reverse

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.tests import sells, shop_products
from apps.business_app.views import shop
from apps.common.baseclass_for_testing import BaseTestClass
from apps.users_app.models.groups import Groups
from model_bakery import baker

from rest_framework import status


@pytest.mark.django_db
class TestDashboardViewSetFunctionalities(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_authenticate(self.user)

    def test_shop_product_investment(self):
        shops = [baker.make(Shop), baker.make(Shop)]

        shop_products_per_shop = baker.random_gen.gen_integer(min_int=1, max_int=10)
        random_equal_cost = baker.random_gen.gen_integer(min_int=10, max_int=20)
        for shop in shops:
            baker.make(
                ShopProducts,
                shop=shop,
                cost_price=random_equal_cost,
                quantity=1,
                _quantity=shop_products_per_shop,
            )

        url = reverse("dashboard-shop-product-investment")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("investments"),
            shop_products_per_shop * random_equal_cost * len(shops),
        )

        # Testing filter by shop
        for shop in shops:
            payload = {"shop": shop.id}
            response = self.client.post(url, data=payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.data.get("investments"),
                shop_products_per_shop * random_equal_cost,
            )

    def test_sell_profits(self):
        sell_group = baker.make(SellGroup)  # Initialy without any discount

        shop_products_sold_qty = baker.random_gen.gen_integer(min_int=1, max_int=10)
        random_equal_cost_price = baker.random_gen.gen_integer(min_int=1, max_int=10)
        random_equal_sell_price = baker.random_gen.gen_integer(min_int=11, max_int=20)

        for _ in range(shop_products_sold_qty):
            baker.make(
                Sell,
                sell_group=sell_group,
                shop_product=baker.make(
                    ShopProducts,
                    cost_price=random_equal_cost_price,
                    sell_price=random_equal_sell_price,
                    quantity=1,
                ),
                quantity=1,
            )

        url = reverse("dashboard-sell-profits")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("result"),
            {
                "frequency": "None",  # No frequency was specified
                "total": shop_products_sold_qty
                * (random_equal_sell_price - random_equal_cost_price),
            },
        )
        self.assertEqual(response.data.get("discounts"), 0)

        # Considering the discount
        sell_group.discount = baker.random_gen.gen_integer(
            min_int=1, max_int=random_equal_cost_price
        )
        sell_group.save()
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("result"),
            {
                "frequency": "None",  # No frequency was specified
                "total": shop_products_sold_qty
                * (random_equal_sell_price - random_equal_cost_price),
            },
        )
        self.assertEqual(response.data.get("discounts"), sell_group.discount)
        self.assertEqual(
            response.data.get("sell_group_ids"),
            [sell_group.id],  # Esto solo viene si el discounts vino diferente de 0
        )
