import pytest
from django.urls import reverse
from datetime import datetime, timedelta


from apps.business_app.models.shop_product_input_group_model import (
    ShopProductInputGroup,
)
from apps.business_app.models.shop_product_input_model import ShopProductInput
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.common.models.generic_log import GenericLog
from apps.users_app.models.groups import Groups
from model_bakery import baker

from rest_framework import status
from freezegun import freeze_time


@pytest.mark.django_db
class TestSellGroupsViewSetFunctionalities(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()

    def test_shop_product_input_group_create_without_any_sell_should_fail(self):
        """ """
        url = reverse("shop-product-input-group-list")
        self.user.groups.add(Groups.SHOP_SELLER)
        payload = {
            "shop_products_input": [],
            "extra_info": "",
        }
        self.client.force_login(self.user)

        response = self.client.post(url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_shop_product_input_group_create_happy_path(self):
        """Prueba que en una entrada de productos se crea un solo
        grupo de entradas y varias entradas asociadas a él, todos con mismo autor."""
        self.user.groups.add(Groups.SHOP_SELLER)
        random_qty = baker.random_gen.gen_integer(min_int=1, max_int=5)
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
        shop_product_input_group_query = ShopProductInputGroup.objects.filter(
            author=self.user
        )
        shop_product_input_query = ShopProductInput.objects.filter(author=self.user)

        # Checking initially all was in 0
        self.assertEqual(shop_product_input_group_query.count(), 0)
        self.assertEqual(shop_product_input_query.count(), 0)

        url = reverse("shop-product-input-group-list")

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            shop_product_input_group_query.filter(author=self.user).count(), 1
        )

        self.assertEqual(
            shop_product_input_query.filter(
                shop_product_input_group=shop_product_input_group_query.first(),
                shop_product_input_group__author=self.user,
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
                f"Entrada del {input_created.for_date.strftime('%d-%h-%Y')}",
            )

        # testing the deletion of a shop product input group
        url = reverse("shop-product-input-group-detail", args=[input_created.id])

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
                f"Entrada del {input_created.for_date.strftime('%d-%h-%Y')} cancelada",
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
        shop_product_input_group_query = ShopProductInputGroup.objects.filter(
            author=self.user
        )
        shop_product_input_query = ShopProductInput.objects.filter(author=self.user)

        # Checking initially all was in 0
        self.assertEqual(shop_product_input_group_query.count(), 0)
        self.assertEqual(shop_product_input_query.count(), 0)

        url = reverse("shop-product-input-group-list")

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
        shop_product_input_group_query = ShopProductInputGroup.objects.filter(
            author=self.user
        )
        shop_product_input_query = ShopProductInput.objects.filter(author=self.user)

        # Checking initially all was in 0
        self.assertEqual(shop_product_input_group_query.count(), 0)
        self.assertEqual(shop_product_input_query.count(), 0)

        url = reverse("shop-product-input-group-list")

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
        shop_product_input_group_query = ShopProductInputGroup.objects.filter(
            author=self.user
        )
        shop_product_input_query = ShopProductInput.objects.filter(author=self.user)

        # Checking initially all was in 0
        self.assertEqual(shop_product_input_group_query.count(), 0)
        self.assertEqual(shop_product_input_query.count(), 0)

        url = reverse("shop-product-input-group-list")

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Checking 'for_date' was set to the payload 'for_date' field
        self.assertEqual(shop_product_input_group_query.count(), 1)
        self.assertEqual(shop_product_input_query.count(), 1)

        created_group = shop_product_input_group_query.first()
        self.assertNotEqual(created_group.for_date, created_group.created_timestamp)
        self.assertEqual(created_group.for_date, payload["for_date"])
