import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop_products import ShopProducts
from apps.clients_app.models.client import Client
from apps.common.baseclass_for_testing import BaseTestClass
from apps.users_app.models.groups import Groups
from model_bakery import baker


@pytest.mark.django_db
class TestSellViewSetFunctionalities(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()

    def test_get_protocol(self):
        """
        Se puede acceder con cualquier rol, siempre y cuando sea un usuario registrado
        """
        url = reverse("sell-products-list")
        allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER, Groups.SHOP_SELLER]

        self._test_permissions(
            url, allowed_roles=allowed_groups, request_using_protocol=self.client.get
        )

    def test_get_one_protocol(self):
        """
        Se puede acceder con cualquier rol, siempre y cuando sea un usuario registrado
        """
        test_sell = baker.make(
            Sell,
            shop_product=baker.make(
                ShopProducts,
                cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
                sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
                quantity=baker.random_gen.gen_integer(min_int=3, max_int=5),
            ),
            quantity=baker.random_gen.gen_integer(min_int=1, max_int=2),
        )
        url = reverse("sell-products-detail", kwargs={"pk": test_sell.id})
        allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER, Groups.SHOP_SELLER]

        self._test_permissions(
            url, allowed_roles=allowed_groups, request_using_protocol=self.client.get
        )

    def test_signals_influence_on_shop_product_quantity(self):
        """
        Solo el SUPER_ADMIN y el SHOP_OWNER pueden introducir datos
        """
        # url = reverse("sell-products-list")
        # self.user.groups.add(Groups.SHOP_SELLER)
        initial_qty = baker.random_gen.gen_integer(min_int=10, max_int=20)
        shop_product = baker.make(
            ShopProducts,
            cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
            sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
            quantity=initial_qty,
        )
        selled_qty = baker.random_gen.gen_integer(min_int=1, max_int=10)

        sell = baker.make(Sell, shop_product=shop_product, quantity=selled_qty)
        shop_product.refresh_from_db()
        self.assertEqual(initial_qty - selled_qty, shop_product.quantity)

        sell.delete()
        shop_product.refresh_from_db()
        self.assertEqual(initial_qty, shop_product.quantity)

    def test_sell_exposes_its_group_client_total_and_note(self):
        """
        Cada venta expone los datos de su grupo (cliente, total y nota) que usa el
        encabezado agrupado de la tabla de ventas.
        """
        client = baker.make(Client, name="Cliente Grupo", phone="5841111111")
        sell_group = baker.make(
            SellGroup,
            client=client,
            total=Decimal("250.75"),
            discount=10,
            extra_info="Entrega en la tarde",
        )
        sell = baker.make(
            Sell,
            sell_group=sell_group,
            shop_product=baker.make(ShopProducts, cost_price=1, sell_price=3, quantity=10),
            quantity=1,
        )
        # SHOP_OWNER is not restricted to the seller shop, so the row is visible.
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        url = reverse("sell-products-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = next(
            item for item in response.json()["results"] if item["id"] == sell.id
        )
        self.assertEqual(data["client_name"], "Cliente Grupo")
        self.assertEqual(data["client_phone"], "5841111111")
        self.assertEqual(Decimal(str(data["group_total"])), Decimal("250.75"))
        self.assertEqual(data["group_extra_info"], "Entrega en la tarde")

    def test_sell_of_group_without_client_exposes_empty_client_name(self):
        """Un grupo sin cliente expone client_name vacio en vez de fallar."""
        sell_group = baker.make(SellGroup, client=None, total=Decimal("80.00"))
        sell = baker.make(
            Sell,
            sell_group=sell_group,
            shop_product=baker.make(ShopProducts, cost_price=1, sell_price=3, quantity=10),
            quantity=1,
        )
        # SHOP_OWNER is not restricted to the seller shop, so the row is visible.
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        url = reverse("sell-products-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = next(
            item for item in response.json()["results"] if item["id"] == sell.id
        )
        self.assertEqual(data["client_name"], "")
