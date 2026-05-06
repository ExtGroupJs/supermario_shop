import pytest
from django.urls import reverse
from datetime import datetime, timedelta


from apps.business_app.models.input_group import (
    InputGroup,
)
from apps.business_app.models.input import Input
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.common.models.generic_log import GenericLog
from apps.users_app.models.groups import Groups
from model_bakery import baker

from rest_framework import status
from freezegun import freeze_time


@pytest.mark.django_db
class TestInputGroupViewSetFunctionalities(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()

    def test_input_group_create_without_any_sell_should_fail(self):
        """ """
        url = reverse("input-groups-list")
        self.user.groups.add(Groups.SHOP_SELLER)
        payload = {
            "shop_products_input": [],
            "extra_info": "",
        }
        self.client.force_login(self.user)

        response = self.client.post(url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_input_group_create_happy_path(self):
        """Prueba que en una entrada de productos se crea un solo
        grupo de entradas y varias entradas asociadas a él, todos con mismo autor."""
        self.user.groups.add(Groups.SHOP_SELLER)
        random_qty = baker.random_gen.gen_integer(min_int=1, max_int=5)
        random_shop_product_qty = baker.random_gen.gen_integer(min_int=0, max_int=5)
        random_shop_product_input_qty = baker.random_gen.gen_integer(
            min_int=1, max_int=10
        )
        ShopProducts.objects.all().delete(
            force_policy=0
        )  # this is because in migrations 0021 and 0022 we create ShopProducts
        shop_products = [
            {
                "shop_product": baker.make(
                    ShopProducts,
                    cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
                    sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
                    quantity=random_shop_product_qty,
                ).id,
                "quantity": random_shop_product_input_qty,
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
            "shop_products_input": shop_products,
            "extra_info": "",
        }
        self.client.force_login(self.user)
        shop_product_input_group_query = InputGroup.objects.filter(author=self.user)
        shop_product_input_query = Input.objects.filter(author=self.user)

        # Checking initially all was in 0
        self.assertEqual(shop_product_input_group_query.count(), 0)
        self.assertEqual(shop_product_input_query.count(), 0)

        url = reverse("input-groups-list")

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            shop_product_input_group_query.filter(author=self.user).count(), 1
        )

        self.assertEqual(
            shop_product_input_query.filter(
                input_group=shop_product_input_group_query.first(),
                input_group__author=self.user,
            ).count(),
            random_qty,
        )
        self.assertEqual(shop_product_input_group_query.count(), 1)

        self.assertEqual(
            ShopProducts.objects.filter(
                quantity=random_shop_product_qty + random_shop_product_input_qty
            ).count(),
            random_qty,
        )
        self.assertEqual(
            GenericLog.objects.filter(
                performed_action=GenericLog.ACTION.CREATED,
                object_id__in=ShopProducts.objects.values_list("id", flat=True),
                extra_log_info__isnull=True,
            ).count(),
            ShopProducts.objects.count(),
        )
        logs_when_input = GenericLog.objects.filter(
            performed_action=GenericLog.ACTION.UPDATED,
            object_id__in=ShopProducts.objects.values_list("id", flat=True),
            extra_log_info__isnull=False,
            created_by=self.user,
        )
        self.assertEqual(
            logs_when_input.count(),
            ShopProducts.objects.count(),
        )
        input_created = shop_product_input_group_query.first()
        for log in logs_when_input:
            self.assertEqual(
                log.extra_log_info,
                f"(Entrada del {input_created.for_date.strftime('%d-%h-%Y')})",
            )

        # testing the deletion of a shop product input group
        url = reverse("input-groups-detail", args=[input_created.id])

        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            ShopProducts.objects.filter(quantity=random_shop_product_qty).count(),
            random_qty,
        )
        self.assertEqual(
            shop_product_input_query.count(),
            0,  # All inputs should be deleted
        )
        self.assertEqual(
            logs_when_input.all().count(),
            ShopProducts.objects.count()
            * 2,  # One for the update (+) and one for the deletion (-)
        )
        latest_logs = logs_when_input.all().order_by("-created_timestamp")[
            :random_qty
        ]  # Logs when deleting
        for log in latest_logs:
            self.assertEqual(
                log.extra_log_info,
                f"(Entrada del {input_created.for_date.strftime('%d-%h-%Y')} cancelada)",
            )

    def test_for_date_must_be_not_future_date(self):
        """"""
        self.user.groups.add(Groups.SHOP_SELLER)
        random_shop_product_qty = baker.random_gen.gen_integer(min_int=0, max_int=5)
        random_shop_product_input_qty = baker.random_gen.gen_integer(
            min_int=1, max_int=10
        )
        shop_products = [
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
            "shop_products_input": shop_products,
            "extra_info": "",
            "for_date": datetime.now() + timedelta(days=1),  # This is set to fail
        }
        self.client.force_login(self.user)
        shop_product_input_group_query = InputGroup.objects.filter(author=self.user)
        shop_product_input_query = Input.objects.filter(author=self.user)

        # Checking initially all was in 0
        self.assertEqual(shop_product_input_group_query.count(), 0)
        self.assertEqual(shop_product_input_query.count(), 0)

        url = reverse("input-groups-list")

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
        random_shop_product_qty = baker.random_gen.gen_integer(min_int=0, max_int=5)
        random_shop_product_input_qty = baker.random_gen.gen_integer(
            min_int=1, max_int=10
        )
        shop_products = [
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
            "shop_products_input": shop_products,
            "extra_info": "",
        }
        self.client.force_login(self.user)
        shop_product_input_group_query = InputGroup.objects.filter(author=self.user)
        shop_product_input_query = Input.objects.filter(author=self.user)

        # Checking initially all was in 0
        self.assertEqual(shop_product_input_group_query.count(), 0)
        self.assertEqual(shop_product_input_query.count(), 0)

        url = reverse("input-groups-list")

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Checking 'for_date' was set by default to the current date
        self.assertEqual(shop_product_input_group_query.count(), 1)
        self.assertEqual(shop_product_input_query.count(), 1)

        created_group = shop_product_input_group_query.first()
        self.assertEqual(created_group.for_date, created_group.created_timestamp)
        self.assertEqual(created_group.for_date, datetime.now())

    @freeze_time(datetime.now())
    def test_for_date_can_be_set_explicitly_to_a_previous_date(self):
        """"""
        self.user.groups.add(Groups.SHOP_SELLER)
        random_shop_product_qty = baker.random_gen.gen_integer(min_int=0, max_int=5)
        random_shop_product_input_qty = baker.random_gen.gen_integer(
            min_int=1, max_int=10
        )
        shop_products = [
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
            "shop_products_input": shop_products,
            "extra_info": "",
            "for_date": datetime.now()
            - timedelta(days=baker.random_gen.gen_integer(1, 10)),
        }
        self.client.force_login(self.user)
        shop_product_input_group_query = InputGroup.objects.filter(author=self.user)
        shop_product_input_query = Input.objects.filter(author=self.user)

        # Checking initially all was in 0
        self.assertEqual(shop_product_input_group_query.count(), 0)
        self.assertEqual(shop_product_input_query.count(), 0)

        url = reverse("input-groups-list")

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Checking 'for_date' was set to the payload 'for_date' field
        self.assertEqual(shop_product_input_group_query.count(), 1)
        self.assertEqual(shop_product_input_query.count(), 1)

        created_group = shop_product_input_group_query.first()
        self.assertNotEqual(created_group.for_date, created_group.created_timestamp)
        self.assertEqual(created_group.for_date, payload["for_date"])

    def test_destroy_input_group_deletes_inputs_and_restores_inventory_with_logs(self):
        """
        Al eliminar un InputGroup se deben eliminar sus Inputs,
        restaurar cantidades en inventario y crear logs con info de cancelacion.
        """
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)

        initial_quantity_1 = 5
        initial_quantity_2 = 8
        input_quantity_1 = 3
        input_quantity_2 = 4

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

        create_url = reverse("input-groups-list")
        payload = {
            "shop_products_input": [
                {
                    "shop_product": shop_product_1.id,
                    "quantity": input_quantity_1,
                },
                {
                    "shop_product": shop_product_2.id,
                    "quantity": input_quantity_2,
                },
            ],
            "extra_info": "",
        }

        create_response = self.client.post(create_url, data=payload, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        created_group = InputGroup.objects.get(author=self.user)
        self.assertEqual(created_group.inputs.count(), 2)

        shop_product_1.refresh_from_db()
        shop_product_2.refresh_from_db()
        self.assertEqual(shop_product_1.quantity, initial_quantity_1 + input_quantity_1)
        self.assertEqual(shop_product_2.quantity, initial_quantity_2 + input_quantity_2)

        destroy_url = reverse("input-groups-detail", args=[created_group.id])
        destroy_response = self.client.delete(destroy_url, format="json")
        self.assertEqual(destroy_response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(InputGroup.objects.filter(id=created_group.id).exists())
        self.assertEqual(Input.objects.filter(input_group=created_group).count(), 0)

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

        expected_entry_log = (
            f"(Entrada del {created_group.for_date.strftime('%d-%h-%Y')})"
        )
        expected_cancel_log = (
            f"(Entrada del {created_group.for_date.strftime('%d-%h-%Y')} cancelada)"
        )

        self.assertEqual(updated_logs_sp1.first().extra_log_info, expected_entry_log)
        self.assertEqual(updated_logs_sp2.first().extra_log_info, expected_entry_log)
        self.assertEqual(updated_logs_sp1.last().extra_log_info, expected_cancel_log)
        self.assertEqual(updated_logs_sp2.last().extra_log_info, expected_cancel_log)

    def test_destroy_input_group_only_deletes_its_own_inputs(self):
        """
        El destroy de un InputGroup solo elimina sus Inputs asociados,
        sin afectar Inputs de otros grupos.
        """
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)

        shop_product_1 = baker.make(
            ShopProducts, quantity=4, cost_price=1, sell_price=3
        )
        shop_product_2 = baker.make(
            ShopProducts, quantity=6, cost_price=1, sell_price=3
        )

        create_url = reverse("input-groups-list")

        first_group_response = self.client.post(
            create_url,
            data={
                "shop_products_input": [
                    {"shop_product": shop_product_1.id, "quantity": 2},
                ],
                "extra_info": "",
            },
            format="json",
        )
        self.assertEqual(first_group_response.status_code, status.HTTP_201_CREATED)

        second_group_response = self.client.post(
            create_url,
            data={
                "shop_products_input": [
                    {"shop_product": shop_product_2.id, "quantity": 1},
                ],
                "extra_info": "",
            },
            format="json",
        )
        self.assertEqual(second_group_response.status_code, status.HTTP_201_CREATED)

        groups = InputGroup.objects.filter(author=self.user).order_by(
            "created_timestamp"
        )
        first_group = groups.first()
        second_group = groups.last()

        self.assertEqual(Input.objects.filter(input_group=first_group).count(), 1)
        self.assertEqual(Input.objects.filter(input_group=second_group).count(), 1)

        destroy_url = reverse("input-groups-detail", args=[first_group.id])
        destroy_response = self.client.delete(destroy_url, format="json")
        self.assertEqual(destroy_response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Input.objects.filter(input_group=first_group).count(), 0)
        self.assertEqual(Input.objects.filter(input_group=second_group).count(), 1)
