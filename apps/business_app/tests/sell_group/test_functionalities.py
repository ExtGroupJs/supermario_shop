import pytest
from django.urls import reverse

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.common.models.generic_log import GenericLog
from apps.users_app.models.groups import Groups
from model_bakery import baker

from rest_framework import status


@pytest.mark.django_db
class TestSellGroupsViewSetFunctionalities(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()

    def test_sell_group_create_without_any_sell_should_fail(self):
        """ """
        url = reverse("sell-groups-list")
        self.user.groups.add(Groups.SHOP_SELLER)
        payload = {
            "discount": 0,
            "extra_info": "",
            "payment_method": "U",
            "seller": self.user.id,
            "sells": [],
        }
        self.client.force_login(self.user)

        response = self.client.post(url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sell_group_create_happy_path(self):
        """Prueba que en una venta con varios productos individuales se crea un solo
        grupo de ventas y varias ventas asociadas a él, todos con mismo vendedor."""
        self.user.groups.add(Groups.SHOP_SELLER)
        random_qty = baker.random_gen.gen_integer(min_int=1, max_int=5)
        random_shop_product_qty = baker.random_gen.gen_integer(min_int=2, max_int=5)
        random_shop_product_selled_qty = baker.random_gen.gen_integer(
            min_int=1, max_int=random_shop_product_qty
        )
        sells = [
            {
                "shop_product": baker.make(
                    ShopProducts,
                    cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
                    sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
                    quantity=random_shop_product_qty,
                ).id,
                "extra_info": "",
                "quantity": random_shop_product_selled_qty,
            }
            for _ in range(random_qty)
        ]
        self.assertEqual(
            ShopProducts.objects.count(),
            GenericLog.objects.filter(
                performed_action=GenericLog.ACTION.CREATED
            ).count(),
        )

        payload = {
            "discount": 0,
            "extra_info": "",
            "payment_method": "U",
            "seller": self.user.id,
            "sells": sells,
        }
        self.client.force_login(self.user)
        sell_group_query = SellGroup.objects.all()
        sell_query = Sell.objects.all()
        self.assertEqual(sell_group_query.count(), 0)
        self.assertEqual(sell_query.count(), 0)

        url = reverse("sell-groups-list")

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(sell_group_query.filter(seller=self.user).count(), 1)

        self.assertEqual(
            sell_query.filter(
                sell_group=sell_group_query.first(), seller=self.user
            ).count(),
            random_qty,
        )
        self.assertEqual(
            ShopProducts.objects.filter(
                quantity=random_shop_product_qty - random_shop_product_selled_qty
            ).count(),
            random_qty,
        )

        self.assertEqual(
            ShopProducts.objects.count(),
            GenericLog.objects.filter(
                performed_action=GenericLog.ACTION.UPDATED
            ).count(),
        )
