import pytest
from django.urls import reverse

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts
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
                sell_price=random_equal_cost + 1,  # is irrelevant for this test
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

    def test_shop_product_investment_filter_by_shop_id(self):
        target_shop = baker.make(Shop)
        other_shop = baker.make(Shop)

        baker.make(
            ShopProducts,
            shop=target_shop,
            cost_price=5,
            sell_price=6,
            quantity=2,
        )
        baker.make(
            ShopProducts,
            shop=target_shop,
            cost_price=3,
            sell_price=4,
            quantity=4,
        )
        baker.make(
            ShopProducts,
            shop=other_shop,
            cost_price=100,
            sell_price=120,
            quantity=1,
        )

        url = reverse("dashboard-shop-product-investment")
        response = self.client.post(
            url, data={"shop_id": target_shop.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("investments"), 22)

    def test_shop_product_filter_by_shop(self):
        wholesale_shop = baker.make(Shop, name=Shop.WHOLESALE_SHOP_NAME)
        shop_products_to_create = baker.random_gen.gen_integer(min_int=1, max_int=10)
        baker.make(
            ShopProducts,
            shop=wholesale_shop,  # these are in the shop, and should be counted when filtering by it
            cost_price=1,
            sell_price=2,
            quantity=1,
            _quantity=shop_products_to_create,
        )
        baker.make(
            ShopProducts,
            cost_price=1,
            sell_price=2,
            quantity=1,
            _quantity=shop_products_to_create,
        )

        url = reverse("shop-products-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = response.json()
        self.assertEqual(response_content.get("count"), shop_products_to_create * 2)

        response = self.client.get(f"{url}?shop={wholesale_shop.id}", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = response.json()
        self.assertEqual(response_content.get("count"), shop_products_to_create)

    def test_shop_product_investment_with_previous_sells(self):
        shop = baker.make(Shop)

        random_equal_cost = baker.random_gen.gen_integer(min_int=10, max_int=20)
        random_qty = baker.random_gen.gen_integer(min_int=10, max_int=20)
        shop_product = baker.make(
            ShopProducts,
            shop=shop,
            sell_price=random_equal_cost + 1,
            cost_price=random_equal_cost,
            quantity=random_qty,
        )
        url = reverse("dashboard-shop-product-investment")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("investments"),
            random_equal_cost
            * random_qty,  # Initial investment only depends on the cost price of the product
        )

        first_sell_qty = random_qty - int(random_qty / 2)
        baker.make(Sell, shop_product=shop_product, quantity=first_sell_qty)

        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("investments"),
            random_equal_cost
            * random_qty,  # despite a part is sold the investment remains
        )
        baker.make(
            Sell, shop_product=shop_product, quantity=random_qty - first_sell_qty
        )
        url = reverse("dashboard-shop-product-investment")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("investments"),
            random_equal_cost
            * random_qty,  # all products sold, the investment is the same
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

    def test_sell_profits_filter_by_shop_id(self):
        target_shop = baker.make(Shop)
        other_shop = baker.make(Shop)

        target_shop_product = baker.make(
            ShopProducts,
            shop=target_shop,
            cost_price=10,
            sell_price=15,
            quantity=10,
        )
        other_shop_product = baker.make(
            ShopProducts,
            shop=other_shop,
            cost_price=1,
            sell_price=10,
            quantity=10,
        )

        baker.make(Sell, shop_product=target_shop_product, quantity=1)
        baker.make(Sell, shop_product=target_shop_product, quantity=2)
        baker.make(Sell, shop_product=other_shop_product, quantity=10)

        url = reverse("dashboard-sell-profits")
        response = self.client.post(
            url, data={"shop_id": target_shop.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("result"),
            {
                "frequency": "None",
                "total": 15,
            },
        )

    def test_shop_product_sells_count_filter_by_shop_id(self):
        target_shop = baker.make(Shop)
        other_shop = baker.make(Shop)

        target_shop_product = baker.make(
            ShopProducts,
            shop=target_shop,
            cost_price=2,
            sell_price=3,
            quantity=20,
        )
        other_shop_product = baker.make(
            ShopProducts,
            shop=other_shop,
            cost_price=2,
            sell_price=3,
            quantity=20,
        )

        baker.make(Sell, shop_product=target_shop_product, quantity=1)
        baker.make(Sell, shop_product=target_shop_product, quantity=5)
        baker.make(Sell, shop_product=other_shop_product, quantity=7)

        url = reverse("dashboard-shop-product-sells-count")
        response = self.client.post(
            url, data={"shop_id": target_shop.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("result"),
            {
                "frequency": "None",
                "total": 2,
            },
        )

    def test_shop_product_sells_products_count_filter_by_shop_id(self):
        target_shop = baker.make(Shop)
        other_shop = baker.make(Shop)

        target_shop_product = baker.make(
            ShopProducts,
            shop=target_shop,
            cost_price=2,
            sell_price=4,
            quantity=20,
        )
        other_shop_product = baker.make(
            ShopProducts,
            shop=other_shop,
            cost_price=2,
            sell_price=4,
            quantity=20,
        )

        baker.make(Sell, shop_product=target_shop_product, quantity=2)
        baker.make(Sell, shop_product=target_shop_product, quantity=3)
        baker.make(Sell, shop_product=other_shop_product, quantity=10)

        url = reverse("dashboard-shop-product-sell-products-count")
        response = self.client.post(
            url, data={"shop_id": target_shop.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("result"),
            {
                "frequency": "None",
                "total": 5,
            },
        )
