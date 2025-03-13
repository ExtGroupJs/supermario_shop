import pytest
from django.urls import reverse
from redis import int_or_str

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.common.models.generic_log import GenericLog
from apps.users_app.models.groups import Groups
from model_bakery import baker
from django.core.management import call_command


from rest_framework import status

from apps.users_app.models.system_user import SystemUser


@pytest.mark.django_db
class TestResetDataCommand(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_authenticate(self.user)
        baker.make(SystemUser, username="dev")

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

        self.assertTrue(
            GenericLog.objects.filter(
                performed_action=GenericLog.ACTION.UPDATED
            ).exists()
        )
        self.assertTrue(Sell.objects.all().exists())
        self.assertTrue(SellGroup.objects.all().exists())

        call_command("reset_data")

        self.assertFalse(
            GenericLog.objects.filter(
                performed_action=GenericLog.ACTION.UPDATED
            ).exists()
        )
        self.assertFalse(Sell.objects.all().exists())
        self.assertFalse(SellGroup.objects.all().exists())

        self.assertEqual(
            GenericLog.objects.filter(
                performed_action=GenericLog.ACTION.CREATED
            ).count(),
            ShopProducts.objects.filter(quantity__gt=0).count(),
        )

        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("result"),
            {
                "frequency": "None",  # No frequency was specified
                "total": None,
            },
        )

    def test_shop_product_investment_remains_the_same_when_removed_sells(self):
        shop = baker.make(Shop)

        random_equal_cost = baker.random_gen.gen_integer(min_int=10, max_int=20)
        random_initial_qty = baker.random_gen.gen_integer(min_int=10, max_int=20)
        shop_product = baker.make(
            ShopProducts,
            shop=shop,
            cost_price=random_equal_cost,
            quantity=random_initial_qty,
        )
        url = reverse("dashboard-shop-product-investment")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            int(response.data.get("investments")),
            random_equal_cost
            * random_initial_qty,  # Initial investment only depends on the cost price of the product
        )

        first_sell_qty = random_initial_qty - int(random_initial_qty / 2)
        baker.make(Sell, shop_product=shop_product, quantity=first_sell_qty)

        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            int(response.data.get("investments")),
            random_equal_cost
            * random_initial_qty,  # despite a part is sold the investment remains
        )
        shop_product.refresh_from_db()

        self.assertEqual(shop_product.quantity, random_initial_qty - first_sell_qty)

        call_command("reset_data")  # all the Sells were deleted

        self.assertEqual(
            shop_product.quantity, random_initial_qty - first_sell_qty
        )  # the signal on Sell was not triggered

        self.assertEqual(Sell.objects.count(), 0)
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            int(response.data.get("investments")),
            random_equal_cost
            * shop_product.quantity,  # now de investment depends on the remaining quantity of the shop_product
        )

    def test_shop_product_investment_remains_the_same_when_removed_sell_groups(self):
        shop = baker.make(Shop)

        random_equal_cost = baker.random_gen.gen_integer(min_int=10, max_int=20)
        random_initial_qty = baker.random_gen.gen_integer(min_int=10, max_int=20)
        shop_product = baker.make(
            ShopProducts,
            shop=shop,
            cost_price=random_equal_cost,
            quantity=random_initial_qty,
        )

        url = reverse("dashboard-shop-product-investment")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            int(response.data.get("investments")),
            random_equal_cost
            * random_initial_qty,  # Initial investment only depends on the cost price of the product
        )

        sell_group = baker.make(SellGroup)
        shop_products_sold_qty = baker.random_gen.gen_integer(
            min_int=1, max_int=random_initial_qty
        )
        for _ in range(shop_products_sold_qty):
            baker.make(
                Sell,
                sell_group=sell_group,
                shop_product=shop_product,
                quantity=1,
            )

        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            int(response.data.get("investments")),
            random_equal_cost
            * random_initial_qty,  # despite a part is sold the investment remains
        )
        shop_product.refresh_from_db()

        self.assertEqual(
            shop_product.quantity, random_initial_qty - shop_products_sold_qty
        )

        call_command("reset_data")  # all the Sells were deleted

        self.assertEqual(
            shop_product.quantity, random_initial_qty - shop_products_sold_qty
        )  # the signal on Sell was not triggered

        self.assertEqual(SellGroup.objects.count(), 0)
        self.assertEqual(Sell.objects.count(), 0)

        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            int(response.data.get("investments")),
            random_equal_cost
            * shop_product.quantity,  # now de investment depends on the remaining quantity of the shop_product
        )
