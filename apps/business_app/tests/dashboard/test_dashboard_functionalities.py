import pytest
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

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

    def test_shop_product_filter_by_shop(self):
        ShopProducts.objects.all().delete(
            force_policy=0
        )  # this is because in migrations 0021 and 0022 we create ShopProducts
        # Migrations 0028/0032 already create the wholesale shop, so reuse it
        # instead of hitting the unique name constraint.
        wholesale_shop, _ = Shop.objects.get_or_create(
            name=Shop.WHOLESALE_SHOP_NAME
        )
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

        # The shop of a group is the shop of its products, so the group has to be
        # reached through a sell of the target shop to be selected by the filter.
        target_sell_group = baker.make(SellGroup)
        other_sell_group = baker.make(SellGroup)
        baker.make(
            Sell,
            sell_group=target_sell_group,
            shop_product=target_shop_product,
            quantity=1,
        )
        baker.make(
            Sell,
            sell_group=target_sell_group,
            shop_product=target_shop_product,
            quantity=2,
        )
        baker.make(
            Sell,
            sell_group=other_sell_group,
            shop_product=other_shop_product,
            quantity=10,
        )

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

    def test_sell_profits_filters_by_group_date_not_by_sell_date(self):
        """
        The dashboard measures the period by the date of the group, not by the date of
        each sell, so a sell added later to an old group is reported in the period of
        the group and never splits the group between two periods.
        """
        shop = baker.make(Shop)
        shop_product = baker.make(
            ShopProducts,
            shop=shop,
            cost_price=2,
            sell_price=4,
            quantity=10,
        )
        sell_group = baker.make(SellGroup)
        baker.make(Sell, sell_group=sell_group, shop_product=shop_product, quantity=1)

        # The sell is dated today, but it belongs to a group of the previous month.
        old_group_day = timezone.now() - timedelta(days=40)
        Sell.objects.filter(sell_group=sell_group).update(
            created_timestamp=timezone.now()
        )
        SellGroup.objects.filter(pk=sell_group.pk).update(
            created_timestamp=old_group_day
        )

        url = reverse("dashboard-sell-profits")

        # No period at all: the group is selected regardless of how old it is.
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("result").get("total"), 2)

        # Asking for the period of the group returns it, even though the sell itself is
        # far newer than that period.
        group_day = old_group_day.date()
        response = self.client.post(
            url,
            data={
                "created_timestamp__gte": group_day.strftime("%Y-%m-%d"),
                "created_timestamp__lte": group_day.strftime("%Y-%m-%d"),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("result").get("total"), 2)

    def test_sell_profits_discount_is_taken_once_per_group(self):
        """
        A discount belongs to the sale, so a group with five sells has its discount
        subtracted once and not once per sell.
        """
        shop = baker.make(Shop)
        shop_product = baker.make(
            ShopProducts,
            shop=shop,
            cost_price=1,
            sell_price=3,
            quantity=10,
        )
        sell_group = baker.make(SellGroup, discount=5)
        baker.make(
            Sell,
            sell_group=sell_group,
            shop_product=shop_product,
            quantity=1,
            _quantity=5,
        )

        url = reverse("dashboard-sell-profits")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("result").get("total"),
            10,  # 5 sells x (3 - 1)
        )
        self.assertEqual(response.data.get("discounts"), 5)
        self.assertEqual(response.data.get("sell_group_ids"), [sell_group.id])

    def test_sell_profits_ignores_sells_without_group(self):
        """
        A sell is part of a sale, so a sell with no group has no sale to be reported in
        and must not add anything to the totals.
        """
        shop = baker.make(Shop)
        shop_product = baker.make(
            ShopProducts,
            shop=shop,
            cost_price=1,
            sell_price=11,
            quantity=10,
        )
        sell_group = baker.make(SellGroup)
        baker.make(Sell, sell_group=sell_group, shop_product=shop_product, quantity=2)
        baker.make(
            Sell,
            sell_group=None,
            shop_product=shop_product,
            quantity=5,
        )

        url = reverse("dashboard-sell-profits")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("result").get("total"),
            20,  # only the 2 units of the grouped sell
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

        # Each sell carries a different quantity on purpose: the tile reports sales,
        # and a sale is a group, so the quantities must not change the count.
        target_first_sell_group = baker.make(SellGroup)
        target_second_sell_group = baker.make(SellGroup)
        other_sell_group = baker.make(SellGroup)
        baker.make(
            Sell,
            sell_group=target_first_sell_group,
            shop_product=target_shop_product,
            quantity=1,
        )
        baker.make(
            Sell,
            sell_group=target_second_sell_group,
            shop_product=target_shop_product,
            quantity=5,
        )
        baker.make(
            Sell,
            sell_group=other_sell_group,
            shop_product=other_shop_product,
            quantity=7,
        )

        url = reverse("dashboard-shop-product-sells-count")
        response = self.client.post(
            url, data={"shop_id": target_shop.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("result"),
            {
                "frequency": "None",
                "total": 2,  # two sales, although they sold 1 + 5 units
            },
        )

    def test_shop_product_sells_count_counts_groups_not_sells(self):
        """
        The tiles report sales, and a sale is the group: a sale of five products is one
        sale and not five.
        """
        shop = baker.make(Shop)
        shop_product = baker.make(
            ShopProducts,
            shop=shop,
            cost_price=1,
            sell_price=2,
            quantity=20,
        )
        # Two sales: one of a single product and another of three products.
        one_product_sale = baker.make(SellGroup)
        baker.make(
            Sell, sell_group=one_product_sale, shop_product=shop_product, quantity=1
        )
        three_products_sale = baker.make(SellGroup)
        baker.make(
            Sell,
            sell_group=three_products_sale,
            shop_product=shop_product,
            quantity=1,
            _quantity=3,
        )

        url = reverse("dashboard-shop-product-sells-count")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("result").get("total"),
            2,  # two sales, although they sold 1 + 3 = 4 lines
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

    def test_money_to_recover_multiplies_sell_price_by_quantity(self):
        """
        The money to recover is the stock of the shop valued at its sell price: every
        product of the shop contributes its sell price times the units it has, and the
        products of another shop are never part of it.
        """
        target_shop = baker.make(Shop, enabled=True)
        other_shop = baker.make(Shop, enabled=True)

        baker.make(
            ShopProducts,
            shop=target_shop,
            cost_price=2,
            sell_price=4,
            quantity=10,
        )
        baker.make(
            ShopProducts,
            shop=target_shop,
            cost_price=2,
            sell_price=5.5,
            quantity=2,
        )
        baker.make(
            ShopProducts,
            shop=other_shop,
            cost_price=2,
            sell_price=100,
            quantity=100,
        )

        url = reverse("dashboard-money-to-recover")
        response = self.client.post(
            url, data={"shop_id": target_shop.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("result").get("total"),
            4 * 10 + 5.5 * 2,
        )

    def test_money_to_recover_only_counts_enabled_shops(self):
        """
        Only the stock of the enabled shops is counted: without a shop the tile skips
        the products of every disabled shop, and a disabled shop cannot even be asked
        for by id, the payload rejects it.
        """
        ShopProducts.objects.all().delete(
            force_policy=0
        )  # this is because in migrations 0021 and 0022 we create ShopProducts
        enabled_shop = baker.make(Shop, enabled=True)
        disabled_shop = baker.make(Shop, enabled=False)
        baker.make(
            ShopProducts,
            shop=enabled_shop,
            cost_price=1,
            sell_price=3,
            quantity=7,
        )
        baker.make(
            ShopProducts,
            shop=disabled_shop,
            cost_price=1,
            sell_price=2.5,
            quantity=4,
        )

        url = reverse("dashboard-money-to-recover")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("result").get("total"),
            3 * 7,  # the stock of the disabled shop is left out
        )

        response = self.client.post(
            url, data={"shop_id": disabled_shop.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("shop_id", response.data)

    def test_dashboard_tiles_reject_disabled_shops(self):
        """
        Every tile of the dashboard only filters by enabled shops: the period tiles and
        the counters turn the id of a disabled shop into a validation error instead of
        reporting money or sales of a shop that is not enabled.
        """
        disabled_shop = baker.make(Shop, enabled=False)

        for url_name in (
            "dashboard-sell-profits",
            "dashboard-sell-group-totals",
            "dashboard-shop-product-sells-count",
            "dashboard-shop-product-sell-products-count",
            "dashboard-money-to-recover",
        ):
            url = reverse(url_name)
            response = self.client.post(
                url, data={"shop_id": disabled_shop.id}, format="json"
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"{url_name} accepted a disabled shop",
            )
            self.assertIn("shop_id", response.data)
