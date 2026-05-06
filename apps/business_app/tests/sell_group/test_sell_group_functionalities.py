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
        ShopProducts.objects.all().delete(
            force_policy=0
        )  # this is because in migrations 0021 and 0022 we create ShopProducts
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
            min_int=2, max_int=random_shop_product_qty
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

    def test_destroy_sell_group_deletes_sells_and_restores_inventory_with_logs(self):
        """
        Al eliminar un SellGroup se deben eliminar sus Sells,
        restaurar cantidades en inventario y crear logs con info de cancelacion.
        """
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)

        initial_quantity_1 = 12
        initial_quantity_2 = 10
        sell_quantity_1 = 4
        sell_quantity_2 = 3

        shop_product_1 = baker.make(
            ShopProducts,
            quantity=initial_quantity_1,
            cost_price=1,
            sell_price=3,
        )
        shop_product_2 = baker.make(
            ShopProducts,
            quantity=initial_quantity_2,
            cost_price=1,
            sell_price=3,
        )

        create_url = reverse("sell-groups-list")
        payload = {
            "discount": 0,
            "extra_info": "",
            "payment_method": "U",
            "sells": [
                {
                    "shop_product": shop_product_1.id,
                    "quantity": sell_quantity_1,
                },
                {
                    "shop_product": shop_product_2.id,
                    "quantity": sell_quantity_2,
                },
            ],
        }

        create_response = self.client.post(create_url, data=payload, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        created_group = SellGroup.objects.get(seller=self.user)
        self.assertEqual(created_group.sells.count(), 2)

        shop_product_1.refresh_from_db()
        shop_product_2.refresh_from_db()
        self.assertEqual(shop_product_1.quantity, initial_quantity_1 - sell_quantity_1)
        self.assertEqual(shop_product_2.quantity, initial_quantity_2 - sell_quantity_2)

        destroy_url = reverse("sell-groups-detail", args=[created_group.id])
        destroy_response = self.client.delete(destroy_url, format="json")
        self.assertEqual(destroy_response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(SellGroup.objects.filter(id=created_group.id).exists())
        self.assertEqual(Sell.objects.filter(sell_group=created_group).count(), 0)

        shop_product_1.refresh_from_db()
        shop_product_2.refresh_from_db()
        self.assertEqual(shop_product_1.quantity, initial_quantity_1)
        self.assertEqual(shop_product_2.quantity, initial_quantity_2)

        updated_logs_sp1 = GenericLog.objects.filter(
            object_id=shop_product_1.id,
            performed_action=GenericLog.ACTION.UPDATED,
            created_by=self.user,
        ).order_by("created_timestamp")
        updated_logs_sp2 = GenericLog.objects.filter(
            object_id=shop_product_2.id,
            performed_action=GenericLog.ACTION.UPDATED,
            created_by=self.user,
        ).order_by("created_timestamp")

        self.assertEqual(updated_logs_sp1.count(), 2)
        self.assertEqual(updated_logs_sp2.count(), 2)

        expected_sell_log = f"(Venta del {created_group.for_date.strftime('%d-%h-%Y')})"
        expected_cancel_log = (
            f"(Venta del {created_group.for_date.strftime('%d-%h-%Y')} cancelada)"
        )

        self.assertEqual(updated_logs_sp1.first().extra_log_info, expected_sell_log)
        self.assertEqual(updated_logs_sp2.first().extra_log_info, expected_sell_log)
        self.assertEqual(updated_logs_sp1.last().extra_log_info, expected_cancel_log)
        self.assertEqual(updated_logs_sp2.last().extra_log_info, expected_cancel_log)

    def test_destroy_sell_group_only_deletes_its_own_sells(self):
        """
        El destroy de un SellGroup solo elimina sus Sells asociados,
        sin afectar Sells de otros grupos.
        """
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)

        shop_product_1 = baker.make(ShopProducts, quantity=15, cost_price=1, sell_price=3)
        shop_product_2 = baker.make(ShopProducts, quantity=20, cost_price=1, sell_price=3)

        create_url = reverse("sell-groups-list")

        first_group_response = self.client.post(
            create_url,
            data={
                "discount": 0,
                "extra_info": "",
                "payment_method": "U",
                "sells": [
                    {"shop_product": shop_product_1.id, "quantity": 2},
                ],
            },
            format="json",
        )
        self.assertEqual(first_group_response.status_code, status.HTTP_201_CREATED)

        second_group_response = self.client.post(
            create_url,
            data={
                "discount": 0,
                "extra_info": "",
                "payment_method": "U",
                "sells": [
                    {"shop_product": shop_product_2.id, "quantity": 2},
                ],
            },
            format="json",
        )
        self.assertEqual(second_group_response.status_code, status.HTTP_201_CREATED)

        groups = SellGroup.objects.filter(seller=self.user).order_by("created_timestamp")
        first_group = groups.first()
        second_group = groups.last()

        self.assertEqual(Sell.objects.filter(sell_group=first_group).count(), 1)
        self.assertEqual(Sell.objects.filter(sell_group=second_group).count(), 1)

        destroy_url = reverse("sell-groups-detail", args=[first_group.id])
        destroy_response = self.client.delete(destroy_url, format="json")
        self.assertEqual(destroy_response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Sell.objects.filter(sell_group=first_group).count(), 0)
        self.assertEqual(Sell.objects.filter(sell_group=second_group).count(), 1)
