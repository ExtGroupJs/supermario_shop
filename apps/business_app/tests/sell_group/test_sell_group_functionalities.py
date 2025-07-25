import pytest
from django.urls import reverse

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.common.models.generic_log import GenericLog
from apps.users_app.models.groups import Groups
from model_bakery import baker
from datetime import datetime, timedelta
from freezegun import freeze_time

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
            "sells": sells,
        }
        self.client.force_login(self.user)
        sell_group_query = SellGroup.objects.filter(seller=self.user)
        sell_query = Sell.objects.filter(seller=self.user)
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
                performed_action=GenericLog.ACTION.UPDATED,
                created_by=self.user,
            ).count(),
        )

    def test_for_date_must_be_not_future_date(self):
        """"""
        self.user.groups.add(Groups.SHOP_SELLER)
        random_shop_product_qty = baker.random_gen.gen_integer(min_int=2, max_int=15)
        random_shop_product_input_qty = baker.random_gen.gen_integer(
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
                "quantity": random_shop_product_input_qty,
            }
        ]

        payload = {
            "discount": 0,
            "extra_info": "",
            "payment_method": "U",
            "sells": sells,
            "for_date": datetime.now() + timedelta(days=1),  # This is set to fail
        }
        self.client.force_login(self.user)
        sell_group_query = SellGroup.objects.filter(seller=self.user)
        sell_query = Sell.objects.filter(seller=self.user)

        # Checking initially all was in 0
        self.assertEqual(sell_group_query.count(), 0)
        self.assertEqual(sell_query.count(), 0)

        url = reverse("sell-groups-list")

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_content = response.json()

        # Checking the only fail in the call was due to 'for_date' field with the expected message
        self.assertTrue(len(response_content) == 1)
        self.assertTrue("for_date" in response_content.keys())
        self.assertEqual(
            response_content["for_date"][0],
            "La fecha de la venta no puede ser mayor al momento actual",
        )

    @freeze_time(datetime.now())
    def test_for_date_is_set_to_current_date_if_not_explicitly_set(self):
        """"""
        self.user.groups.add(Groups.SHOP_SELLER)
        random_shop_product_qty = baker.random_gen.gen_integer(min_int=2, max_int=15)
        random_shop_product_input_qty = baker.random_gen.gen_integer(
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
                "quantity": random_shop_product_input_qty,
            }
        ]

        payload = {  # payload without explicit "for_date" field
            "discount": 0,
            "extra_info": "",
            "payment_method": "U",
            "sells": sells,
        }
        self.client.force_login(self.user)
        sell_group_query = SellGroup.objects.filter(seller=self.user)
        sell_query = Sell.objects.filter(seller=self.user)

        # Checking initially all was in 0
        self.assertEqual(sell_group_query.count(), 0)
        self.assertEqual(sell_query.count(), 0)

        url = reverse("sell-groups-list")

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Checking 'for_date' was set by default to the current date
        self.assertEqual(sell_group_query.count(), 1)
        self.assertEqual(sell_query.count(), 1)

        created_group = sell_group_query.first()
        self.assertEqual(created_group.for_date, created_group.created_timestamp)
        self.assertEqual(created_group.for_date, datetime.now())

    @freeze_time(datetime.now())
    def test_for_date_can_be_set_explicitly_to_a_previous_date(self):
        """"""
        self.user.groups.add(Groups.SHOP_SELLER)
        random_shop_product_qty = baker.random_gen.gen_integer(min_int=2, max_int=15)
        random_shop_product_input_qty = baker.random_gen.gen_integer(
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
                "quantity": random_shop_product_input_qty,
            }
        ]

        payload = {
            "discount": 0,
            "extra_info": "",
            "payment_method": "U",
            "sells": sells,
            "for_date": datetime.now()
            - timedelta(days=baker.random_gen.gen_integer(1, 10)),
        }
        self.client.force_login(self.user)
        sell_group_query = SellGroup.objects.filter(seller=self.user)
        sell_query = Sell.objects.filter(seller=self.user)

        # Checking initially all was in 0
        self.assertEqual(sell_group_query.count(), 0)
        self.assertEqual(sell_query.count(), 0)

        url = reverse("sell-groups-list")

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Checking 'for_date' was set to the payload 'for_date' field
        self.assertEqual(sell_group_query.count(), 1)
        self.assertEqual(sell_query.count(), 1)

        created_group = sell_group_query.first()
        self.assertNotEqual(created_group.for_date, created_group.created_timestamp)
        self.assertEqual(created_group.for_date, payload["for_date"])

    def test_selled_qty_greater_than_disponibility_should_raise_400_error(self):
        """"""
        self.user.groups.add(Groups.SHOP_SELLER)
        random_shop_product_qty = baker.random_gen.gen_integer(min_int=2, max_int=15)

        sells = [
            {
                "shop_product": baker.make(
                    ShopProducts,
                    cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
                    sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
                    quantity=random_shop_product_qty,
                ).id,
                "quantity": random_shop_product_qty + 1,
            }
        ]

        payload = {
            "discount": 0,
            "extra_info": "",
            "payment_method": "U",
            "sells": sells,
        }
        self.client.force_login(self.user)
        sell_group_query = SellGroup.objects.filter(seller=self.user)
        sell_query = Sell.objects.filter(seller=self.user)

        # Checking initially all was in 0
        self.assertEqual(sell_group_query.count(), 0)
        self.assertEqual(sell_query.count(), 0)

        url = reverse("sell-groups-list")

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_content = response.json()
        # Checking the only fail in the call was due to 'for_date' field with the expected message
        self.assertTrue(len(response_content) == 1)
        self.assertTrue("sells" in response_content.keys())
        sell_errors = response_content["sells"]
        self.assertTrue("non_field_errors" in sell_errors[0].keys())

        self.assertEqual(
            sell_errors[0]["non_field_errors"][0],
            "La cantidad solicitada es mayor que la disponibilidad.",
        )

    def test_selled_qty_0_should_raise_400_error(self):
        """"""
        self.user.groups.add(Groups.SHOP_SELLER)
        random_shop_product_qty = baker.random_gen.gen_integer(min_int=2, max_int=15)

        sells = [
            {
                "shop_product": baker.make(
                    ShopProducts,
                    cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
                    sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
                    quantity=random_shop_product_qty,
                ).id,
                "quantity": 0,
            }
        ]

        payload = {
            "discount": 0,
            "extra_info": "",
            "payment_method": "U",
            "sells": sells,
        }
        self.client.force_login(self.user)
        sell_group_query = SellGroup.objects.filter(seller=self.user)
        sell_query = Sell.objects.filter(seller=self.user)

        # Checking initially all was in 0
        self.assertEqual(sell_group_query.count(), 0)
        self.assertEqual(sell_query.count(), 0)

        url = reverse("sell-groups-list")

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_content = response.json()
        # Checking the only fail in the call was due to 'for_date' field with the expected message
        self.assertTrue(len(response_content) == 1)
        self.assertTrue("sells" in response_content.keys())
        sell_errors = response_content["sells"]
        self.assertTrue("quantity" in sell_errors[0].keys())

        self.assertEqual(
            sell_errors[0]["quantity"][0],
            "La venta debe ser de al menos un elemento",
        )
