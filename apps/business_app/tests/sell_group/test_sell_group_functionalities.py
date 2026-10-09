import pytest
from django.urls import reverse

from apps.business_app.models.product import Product
from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts
from apps.clients_app.models.client import Client
from apps.common.baseclass_for_testing import BaseTestClass
from apps.common.models.generic_log import GenericLog
from apps.users_app.models.groups import Groups
from model_bakery import baker
from datetime import datetime, timedelta
from decimal import Decimal
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

        expected_sell_log = f"(Venta {created_group.id})"
        expected_cancel_log = (
            f"(Venta {created_group.id} cancelada)"
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

        shop_product_1 = baker.make(
            ShopProducts, quantity=15, cost_price=1, sell_price=3
        )
        shop_product_2 = baker.make(
            ShopProducts, quantity=20, cost_price=1, sell_price=3
        )

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

        groups = SellGroup.objects.filter(seller=self.user).order_by(
            "created_timestamp"
        )
        first_group = groups.first()
        second_group = groups.last()

        self.assertEqual(Sell.objects.filter(sell_group=first_group).count(), 1)
        self.assertEqual(Sell.objects.filter(sell_group=second_group).count(), 1)

        destroy_url = reverse("sell-groups-detail", args=[first_group.id])
        destroy_response = self.client.delete(destroy_url, format="json")
        self.assertEqual(destroy_response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Sell.objects.filter(sell_group=first_group).count(), 0)
        self.assertEqual(Sell.objects.filter(sell_group=second_group).count(), 1)

    def _make_sell_payload(self, shop="keep", **extra):
        """Builds the minimum valid payload of one sell to reuse across client tests.

        ``shop="keep"`` lets model_bakery randomize the shop, so tests that do not care
        about the shop are not coupled to the seller one.
        """
        shop_kwarg = {} if shop == "keep" else {"shop": shop}
        shop_product = baker.make(
            ShopProducts,
            **shop_kwarg,
            cost_price=1,
            sell_price=3,
            quantity=baker.random_gen.gen_integer(min_int=2, max_int=10),
        )
        payload = {
            "discount": 0,
            "extra_info": "",
            "payment_method": "U",
            "sells": [
                {
                    "shop_product": shop_product.id,
                    "quantity": 1,
                },
            ],
        }
        payload.update(extra)
        self.sold_shop_product = shop_product
        return payload

    def test_create_sell_group_with_client_phone_creates_client(self):
        """Al enviar client_name y client_phone se crea el Client y se asigna al SellGroup."""
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)
        client_name = self.faker.name()
        client_phone = f"58{self.faker.random_int(min=1000000, max=9999999)}"

        url = reverse("sell-groups-list")
        response = self.client.post(
            url,
            data=self._make_sell_payload(
                shop=self.user.shop,
                client_name=client_name,
                client_phone=client_phone,
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_client = Client.objects.get(phone=client_phone)
        self.assertEqual(created_client.name, client_name)
        self.assertEqual(created_client.shop, self.sold_shop_product.shop)

        created_group = SellGroup.objects.get(id=response.json()["id"])
        self.assertEqual(created_group.client, created_client)

        # client_name / client_phone are write only, so they must not leak in responses
        self.assertNotIn("client_name", response.json())
        self.assertNotIn("client_phone", response.json())

    def test_create_sell_group_with_existing_client_phone_updates_its_name(self):
        """Si el teléfono ya existe se reutiliza el Client y solo se actualiza el nombre."""
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)
        old_name = self.faker.name()
        new_name = self.faker.name()
        client_phone = f"58{self.faker.random_int(min=1000000, max=9999999)}"
        existing_client = baker.make(Client, name=old_name, phone=client_phone)

        url = reverse("sell-groups-list")
        response = self.client.post(
            url,
            data=self._make_sell_payload(
                client_name=new_name, client_phone=client_phone
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Client.objects.filter(phone=client_phone).count(), 1)
        existing_client.refresh_from_db()
        self.assertEqual(existing_client.name, new_name)

        created_group = SellGroup.objects.get(id=response.json()["id"])
        self.assertEqual(created_group.client, existing_client)

    def test_create_sell_group_without_client_fields_keeps_client_empty(self):
        """Sin client_name ni client_phone el SellGroup se crea sin client (retrocompatible)."""
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)

        url = reverse("sell-groups-list")
        response = self.client.post(url, data=self._make_sell_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_group = SellGroup.objects.get(id=response.json()["id"])
        self.assertIsNone(created_group.client)
        self.assertEqual(Client.objects.count(), 0)

    def test_create_sell_group_client_belongs_to_the_shop_of_the_sold_product(self):
        """El Client se crea en el shop del primer shop_product, no en el del vendedor."""
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)
        other_shop = baker.make(Shop, name=self.faker.unique.company())
        self.assertNotEqual(other_shop, self.user.shop)

        client_phone = f"58{self.faker.random_int(min=1000000, max=9999999)}"
        payload = self._make_sell_payload(
            shop=other_shop,
            client_name=self.faker.name(),
            client_phone=client_phone,
        )

        url = reverse("sell-groups-list")
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_client = Client.objects.get(phone=client_phone)
        self.assertEqual(created_client.shop, other_shop)

        created_group = SellGroup.objects.get(id=response.json()["id"])
        self.assertEqual(created_group.client, created_client)

    def test_create_sell_group_stores_the_total_sent_by_the_view(self):
        """El total enviado por la vista (suma de importes) se guarda en SellGroup.total."""
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)

        url = reverse("sell-groups-list")
        response = self.client.post(
            url,
            data=self._make_sell_payload(total="125.50"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_group = SellGroup.objects.get(id=response.json()["id"])
        self.assertEqual(created_group.total, Decimal("125.50"))
        self.assertEqual(response.json()["total"], "125.50")

    def test_create_sell_group_total_defaults_to_zero_when_not_sent(self):
        """Si la vista no manda total, el grupo se crea con 0.00."""
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)

        url = reverse("sell-groups-list")
        response = self.client.post(url, data=self._make_sell_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_group = SellGroup.objects.get(id=response.json()["id"])
        self.assertEqual(created_group.total, Decimal("0.00"))

    def _make_group_for_report(self, **kwargs):
        """Sell group with one sell, ready to be reported."""
        sell_group = baker.make(SellGroup, **kwargs)
        baker.make(
            Sell,
            sell_group=sell_group,
            shop_product=baker.make(
                ShopProducts,
                product=baker.make(Product, name="Filtro de Aire"),
                cost_price=1,
                sell_price=Decimal("10.00"),
                quantity=50,
            ),
            quantity=3,
        )
        return sell_group

    def test_report_renders_the_receipt_lines_of_the_sell_group(self):
        """El informe reproduce el comprobante que se genera al crear la venta."""
        sell_group = self._make_group_for_report(
            total=Decimal("30.00"),
            discount=5,
            extra_info="Entrega en la tarde",
            payment_method=SellGroup.PAYMENT_METODS.ZELLE,
        )
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        url = reverse("sell-groups-report", kwargs={"pk": sell_group.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        report = response.json()["report"]
        lines = report.split("\n")
        self.assertEqual(lines[0], "COMPROBANTE DE VENTA")
        self.assertIn(f"Nro: {sell_group.id}", report)
        self.assertIn("Metodo de pago: Zelle", report)
        self.assertIn("1. Filtro de Aire", report)
        self.assertIn("   Cantidad: 3", report)
        self.assertIn("   Precio: $10.00", report)
        self.assertIn("   Subtotal: $30.00", report)
        self.assertIn("Subtotal: $30.00", report)
        self.assertIn("Descuento: $5.00", report)
        self.assertIn("Total: $25.00", report)
        self.assertIn("Notas: Entrega en la tarde", report)

    def test_report_shows_the_client_name_without_the_shop(self):
        """El comprobante muestra el nombre del cliente, no el __str__ con la tienda."""
        client = baker.make(Client, name="Juan Perez", phone="5841111111")
        sell_group = self._make_group_for_report(total=Decimal("30.00"), client=client)
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        url = reverse("sell-groups-report", kwargs={"pk": sell_group.id})
        report = self.client.get(url).json()["report"]
        self.assertIn("Cliente: Juan Perez\n", report)

    def test_report_of_a_group_without_client_leaves_the_line_empty(self):
        """Un grupo sin cliente no rompe el informe."""
        sell_group = self._make_group_for_report(total=Decimal("30.00"), client=None)
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        url = reverse("sell-groups-report", kwargs={"pk": sell_group.id})
        report = self.client.get(url).json()["report"]
        self.assertIn("Cliente: \n", report)

    def test_report_of_a_group_without_sells_has_an_empty_products_block(self):
        """Un grupo sin ventas informa cero en vez de reventar."""
        sell_group = baker.make(SellGroup, total=Decimal("0.00"))
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        url = reverse("sell-groups-report", kwargs={"pk": sell_group.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        report = response.json()["report"]
        self.assertIn("PRODUCTOS:\n", report)
        self.assertIn("Total: $0.00", report)

    def test_report_never_reports_a_negative_total(self):
        """Un descuento mayor que el total se recorta en cero."""
        sell_group = self._make_group_for_report(total=Decimal("10.00"), discount=50)
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        url = reverse("sell-groups-report", kwargs={"pk": sell_group.id})
        report = self.client.get(url).json()["report"]
        self.assertIn("Total: $0.00", report)

    def test_report_endpoint_follows_the_same_permissions_as_the_sell_group_list(self):
        """
        El informe no abre permisos nuevos: el action hereda los del viewset, asi que
        SHOP_SELLER (que ya puede ver el listado) tambien puede generar el comprobante.
        """
        sell_group = self._make_group_for_report(total=Decimal("30.00"))
        url = reverse("sell-groups-report", kwargs={"pk": sell_group.id})

        allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER, Groups.SHOP_SELLER]
        self._test_permissions(
            url, allowed_roles=allowed_groups, request_using_protocol=self.client.get
        )

    def _make_group_at(self, when, **kwargs):
        """Sell group dated at ``when``, ready to be reported."""
        return self._make_group_for_report(for_date=when, **kwargs)

    def _period_report(self, **params):
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)
        return self.client.get(reverse("sell-groups-period-report"), params)

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_defaults_to_today_when_no_date_is_sent(self):
        """Sin fechas el reporte trae los grupos de HOY, no los de todo el historico."""
        self._make_group_at(datetime(2026, 3, 10, 9, 0), total=Decimal("50.00"))
        self._make_group_at(datetime(2026, 3, 9, 9, 0), total=Decimal("999.00"))

        response = self._period_report()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["start_date"], "2026-03-10")
        self.assertEqual(response.json()["end_date"], "2026-03-10")
        self.assertEqual(response.json()["groups"], 1)
        self.assertNotIn("$999.00", response.json()["report"])

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_lists_one_line_per_sell_group_and_ends_with_the_total(self):
        """Cada grupo aporta su monto neto y el TOTAL suma esos montos."""
        self._make_group_at(datetime(2026, 3, 10, 9, 0), total=Decimal("50.00"))
        self._make_group_at(
            datetime(2026, 3, 10, 11, 0), total=Decimal("30.00"), discount=5
        )

        report = self._period_report().json()["report"]

        self.assertIn("$50.00", report)
        self.assertIn("$25.00", report)
        self.assertIn("TOTAL: $75.00", report)
        # El monto del reporte es el neto, el descuento no se vuelve a sumar.
        self.assertNotIn("TOTAL: $85.00", report)

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_shows_the_readable_payment_method_of_each_group(self):
        """La linea de grupo imprime el medio de pago legible, no el codigo de la choice."""
        self._make_group_at(
            datetime(2026, 3, 10, 9, 0),
            total=Decimal("50.00"),
            payment_method=SellGroup.PAYMENT_METODS.ZELLE,
        )
        self._make_group_at(
            datetime(2026, 3, 10, 11, 0),
            total=Decimal("30.00"),
            payment_method=SellGroup.PAYMENT_METODS.USD,
        )

        report = self._period_report().json()["report"]

        self.assertIn("Total: $50.00 Zelle", report)
        self.assertIn("Total: $30.00 USD", report)
        # El codigo crudo de la choice ("Z") no llega a quien lee el reporte.
        self.assertNotIn("$50.00 Z\n", report)

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_shows_the_period_on_the_line_above_the_groups(self):
        """La fecha va en la linea superior, antes de la lista de grupos."""
        self._make_group_at(datetime(2026, 3, 10, 9, 0), total=Decimal("50.00"))

        lines = (
            self._period_report(start_date="2026-03-01", end_date="2026-03-10")
            .json()["report"]
            .split("\n")
        )

        period_line = next(
            i for i, line in enumerate(lines) if line.startswith("Periodo:")
        )
        first_group_line = next(
            i for i, line in enumerate(lines) if line.startswith("Id:")
        )
        total_line = next(
            i for i, line in enumerate(lines) if line.startswith("TOTAL:")
        )
        self.assertLess(period_line, first_group_line)
        self.assertLess(first_group_line, total_line)
        self.assertIn("01-Mar-2026", lines[period_line])
        self.assertIn("10-Mar-2026", lines[period_line])

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_only_sums_the_sell_groups_not_the_individual_sells(self):
        """
        Un grupo vale su total UNA vez, por mas productos que tenga, y un grupo sin
        ventas sigue summing lo que el grupo guardo.
        """
        group_with_many_sells = self._make_group_at(
            datetime(2026, 3, 10, 9, 0), total=Decimal("80.00")
        )
        for _ in range(3):
            baker.make(
                Sell,
                sell_group=group_with_many_sells,
                shop_product=baker.make(
                    ShopProducts,
                    product=baker.make(Product),
                    cost_price=1,
                    sell_price=Decimal("10.00"),
                    quantity=50,
                ),
                quantity=2,
            )
        # El grupo cuenta aunque se le borren todas sus ventas individuales.
        orphan_group = self._make_group_at(
            datetime(2026, 3, 10, 10, 0), total=Decimal("20.00")
        )
        orphan_group.sells.all().delete()

        report = self._period_report().json()["report"]

        self.assertIn("TOTAL: $100.00", report)
        self.assertEqual(report.count("Id: "), 2)

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_excludes_the_groups_outside_the_period(self):
        """Las fechas acotan el reporte: antes y despues quedan fuera."""
        self._make_group_at(datetime(2026, 3, 5, 9, 0), total=Decimal("999.00"))
        self._make_group_at(datetime(2026, 3, 8, 9, 0), total=Decimal("40.00"))
        self._make_group_at(datetime(2026, 3, 12, 9, 0), total=Decimal("777.00"))

        response = self._period_report(start_date="2026-03-07", end_date="2026-03-10")

        self.assertEqual(response.json()["groups"], 1)
        self.assertIn("TOTAL: $40.00", response.json()["report"])

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_without_sales_in_the_period_reports_zero(self):
        """Un periodo sin ventas no revienta: informa cero grupos."""
        self._make_group_at(datetime(2026, 1, 1, 9, 0), total=Decimal("999.00"))

        report = self._period_report().json()["report"]

        self.assertIn("Sin ventas en el periodo", report)
        self.assertIn("TOTAL: $0.00", report)

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_never_reports_a_negative_amount(self):
        """Un descuento mayor que el total se recorta en cero."""
        self._make_group_at(
            datetime(2026, 3, 10, 9, 0), total=Decimal("10.00"), discount=50
        )

        report = self._period_report().json()["report"]

        self.assertIn("Total: $0.00", report)
        self.assertIn("TOTAL: $0.00", report)

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_rejects_a_start_date_after_the_end_date(self):
        """Un 'Desde' posterior al 'Hasta' se rechaza en vez de reportar un periodo vacio."""
        self._make_group_at(datetime(2026, 3, 10, 9, 0), total=Decimal("50.00"))

        response = self._period_report(start_date="2026-03-10", end_date="2026-03-01")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no puede ser mayor", response.json()["detail"])
        self.assertNotIn("report", response.json())

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_accepts_a_start_date_equal_to_the_end_date(self):
        """Un solo dia es un periodo valido: Desde igual a Hasta no es un error."""
        self._make_group_at(datetime(2026, 3, 10, 9, 0), total=Decimal("50.00"))

        response = self._period_report(start_date="2026-03-10", end_date="2026-03-10")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("TOTAL: $50.00", response.json()["report"])

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_rejects_an_inverted_period_even_without_a_start_date(self):
        """El 'Hasta' invertido tambien se rechaza: sin 'Desde' cae en hoy."""
        self._make_group_at(datetime(2026, 3, 10, 9, 0), total=Decimal("50.00"))

        response = self._period_report(end_date="2026-03-01")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no puede ser mayor", response.json()["detail"])

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_only_includes_the_groups_of_the_requested_shop(self):
        """El reporte respeta la tienda seleccionada en el selector global."""
        requested_shop = baker.make(Shop)
        other_shop = baker.make(Shop)
        mine = self._make_group_for_report(
            for_date=datetime(2026, 3, 10, 9, 0), total=Decimal("50.00")
        )
        theirs = self._make_group_for_report(
            for_date=datetime(2026, 3, 10, 10, 0), total=Decimal("900.00")
        )
        # update() no traverses relations, so the sells are pointed at their own shop.
        for sell in theirs.sells.all():
            sell.shop_product.shop = requested_shop
            sell.shop_product.save()
        for sell in mine.sells.all():
            sell.shop_product.shop = other_shop
            sell.shop_product.save()

        report = self._period_report(shop=requested_shop.id).json()["report"]

        self.assertIn("$900.00", report)
        self.assertNotIn("$50.00", report)

    @freeze_time("2026-03-10 12:00:00")
    def test_period_report_follows_the_same_permissions_as_the_sell_group_list(self):
        """El reporte no abre permisos nuevos: hereda los permisos del viewset."""
        url = reverse("sell-groups-period-report")

        allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER, Groups.SHOP_SELLER]
        self._test_permissions(
            url, allowed_roles=allowed_groups, request_using_protocol=self.client.get
        )

    # ------------------------------------------------------------------
    # Listing: filters, search and ordering declared on the viewset
    # ------------------------------------------------------------------

    def _login_as_seller(self):
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)

    def _make_group_with_sells(self, shop_product, quantities, **kwargs):
        """Sell group holding one sell per quantity, ready to be listed."""
        sell_group = baker.make(SellGroup, **kwargs)
        for quantity in quantities:
            baker.make(
                Sell,
                sell_group=sell_group,
                shop_product=shop_product,
                quantity=quantity,
            )
        return sell_group

    def test_list_search_returns_the_group_once_when_several_sells_match(self):
        """La busqueda recorre los sells del grupo: dos lineas del mismo producto
        no deben repetir el grupo en el listado."""
        matching_shop_product = baker.make(
            ShopProducts,
            product=baker.make(Product, name="Filtro de Aceite"),
            cost_price=1,
            sell_price=Decimal("10.00"),
            quantity=50,
        )
        other_shop_product = baker.make(
            ShopProducts,
            product=baker.make(Product, name="Bujia de Encendido"),
            cost_price=1,
            sell_price=Decimal("10.00"),
            quantity=50,
        )
        wanted = self._make_group_with_sells(matching_shop_product, [2, 3])
        self._make_group_with_sells(other_shop_product, [1])
        self._login_as_seller()

        response = self.client.get(
            reverse("sell-groups-list"), {"search": "Filtro de Aceite"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["id"], wanted.id)

    def test_list_filters_by_shop_through_the_sells_without_repeating_groups(self):
        """El filtro de tienda se resuelve a traves de los sells, asi que un grupo
        con varias ventas en esa tienda se devuelve una sola vez."""
        requested_shop = baker.make(Shop)
        product_in_shop = baker.make(
            ShopProducts,
            shop=requested_shop,
            product=baker.make(Product, name="Pastillas de Freno"),
            cost_price=1,
            sell_price=Decimal("10.00"),
            quantity=50,
        )
        product_in_other_shop = baker.make(
            ShopProducts,
            product=baker.make(Product, name="Disco de Freno"),
            cost_price=1,
            sell_price=Decimal("10.00"),
            quantity=50,
        )
        wanted = self._make_group_with_sells(product_in_shop, [2, 3])
        self._make_group_with_sells(product_in_other_shop, [1])
        self._login_as_seller()

        response = self.client.get(
            reverse("sell-groups-list"),
            {"sells__shop_product__shop": requested_shop.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["id"], wanted.id)

    def test_list_filters_by_for_date_and_seller(self):
        """Los lookups declarados en ``filterset_fields`` filtran el listado."""
        shop_product = baker.make(
            ShopProducts,
            product=baker.make(Product, name="Filtro de Aire"),
            cost_price=1,
            sell_price=Decimal("10.00"),
            quantity=50,
        )
        today_group = self._make_group_with_sells(
            shop_product, [1], for_date=datetime(2026, 3, 10, 9, 0), seller=self.user
        )
        older_group = self._make_group_with_sells(
            shop_product, [1], for_date=datetime(2026, 3, 9, 9, 0)
        )
        self._login_as_seller()
        url = reverse("sell-groups-list")

        by_date = self.client.get(url, {"for_date__date": "2026-03-10"}).json()
        self.assertEqual(by_date["count"], 1)
        self.assertEqual(by_date["results"][0]["id"], today_group.id)

        by_seller = self.client.get(url, {"seller": self.user.id}).json()
        self.assertEqual(by_seller["count"], 1)
        self.assertEqual(by_seller["results"][0]["id"], today_group.id)

        by_total = self.client.get(url, {"for_date__date__lte": "2026-03-09"}).json()
        self.assertEqual(by_total["count"], 1)
        self.assertEqual(by_total["results"][0]["id"], older_group.id)

    def test_list_ordering_ignores_fields_that_are_not_in_the_model(self):
        """``client_name`` y ``sells`` salen del serializer, no de la tabla: no
        deben ordenar (ni reventar con un 500) cuando llegan en el query string."""
        self._make_group_for_report()
        self._login_as_seller()
        url = reverse("sell-groups-list")

        for ordering in ("client_name", "sells", "-for_date", "total"):
            response = self.client.get(url, {"ordering": ordering})
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                msg=f"ordering=<{ordering}> returned {response.status_code}",
            )
