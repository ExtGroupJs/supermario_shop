import pytest
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
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
            shop_product=baker.make(
                ShopProducts, cost_price=1, sell_price=3, quantity=10
            ),
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
            shop_product=baker.make(
                ShopProducts, cost_price=1, sell_price=3, quantity=10
            ),
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

    def _make_group_with_sell(self, total, discount=0, extra_info="", extra_sells=0):
        sell_group = baker.make(
            SellGroup, total=total, discount=discount, extra_info=extra_info
        )
        sell = baker.make(
            Sell,
            sell_group=sell_group,
            shop_product=baker.make(
                ShopProducts,
                cost_price=1,
                sell_price=Decimal("10.00"),
                quantity=50,
            ),
            quantity=3,
        )
        # Sells that keep the group alive when the tested sell is removed: a group
        # without sells is deleted together with its last one.
        for _ in range(extra_sells):
            baker.make(
                Sell,
                sell_group=sell_group,
                shop_product=baker.make(
                    ShopProducts,
                    cost_price=1,
                    sell_price=Decimal("10.00"),
                    quantity=50,
                ),
                quantity=1,
            )
        return sell_group, sell

    def test_destroy_sell_appends_cancellation_note_to_its_group(self):
        """Al borrar una venta, su grupo queda anotado con BORRADO producto fecha."""
        sell_group, sell = self._make_group_with_sell(
            total=Decimal("30.00"), extra_info="Entrega en la tarde", extra_sells=1
        )
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        url = reverse("sell-products-detail", kwargs={"pk": sell.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Sell.objects.filter(id=sell.id).exists())

        # The group survives because it still has another sell.
        sell_group.refresh_from_db()
        product = sell.shop_product.product.__str__()
        today = timezone.now().strftime("%d-%b-%Y")
        self.assertEqual(
            sell_group.extra_info,
            f"Entrega en la tarde\nBORRADO {product} {today}",
        )

    def test_destroy_sell_reduces_the_group_total_by_the_removed_amount(self):
        """El total del grupo descuenta lo que aportaba la venta borrada."""
        sell_group, sell = self._make_group_with_sell(
            total=Decimal("30.00"), extra_sells=1
        )
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        url = reverse("sell-products-detail", kwargs={"pk": sell.id})
        self.client.delete(url)

        sell_group.refresh_from_db()
        # 3 units x 10.00 sell price were removed out of a 30.00 group total.
        self.assertEqual(sell_group.total, Decimal("0.00"))

    def test_destroy_sell_never_leaves_the_group_total_negative(self):
        """Un total desincronizado no puede dejar al grupo en negativo."""
        sell_group, sell = self._make_group_with_sell(
            total=Decimal("5.00"), extra_sells=1
        )
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        url = reverse("sell-products-detail", kwargs={"pk": sell.id})
        self.client.delete(url)

        sell_group.refresh_from_db()
        self.assertEqual(sell_group.total, Decimal("0.00"))

    def test_destroying_every_sell_of_a_group_keeps_one_note_per_line(self):
        """Cada baja agrega su propio renglón, sin pisar las anteriores."""
        sell_group, first_sell = self._make_group_with_sell(
            total=Decimal("60.00"), extra_info="Nota inicial", extra_sells=1
        )
        second_sell = baker.make(
            Sell,
            sell_group=sell_group,
            shop_product=baker.make(
                ShopProducts, cost_price=1, sell_price=Decimal("10.00"), quantity=50
            ),
            quantity=3,
        )
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        for sell in (first_sell, second_sell):
            url = reverse("sell-products-detail", kwargs={"pk": sell.id})
            self.client.delete(url)

        # The third sell keeps the group alive, so the notes are still readable.
        sell_group.refresh_from_db()
        lines = sell_group.extra_info.split("\n")
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], "Nota inicial")
        self.assertTrue(lines[1].startswith("BORRADO "))
        self.assertTrue(lines[2].startswith("BORRADO "))
        self.assertEqual(sell_group.total, Decimal("0.00"))

    def test_destroy_last_sell_of_a_group_removes_the_empty_group(self):
        """El grupo no sobrevive a su ultima venta: se borra junto con ella."""
        sell_group, sell = self._make_group_with_sell(total=Decimal("30.00"))
        shop_product = sell.shop_product
        shop_product.refresh_from_db()
        quantity_after_selling = shop_product.quantity
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        url = reverse("sell-products-detail", kwargs={"pk": sell.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Sell.objects.filter(id=sell.id).exists())
        self.assertFalse(SellGroup.objects.filter(id=sell_group.id).exists())
        # The inventory restore still happens for the cancelled sell.
        shop_product.refresh_from_db()
        self.assertEqual(
            shop_product.quantity, quantity_after_selling + sell.quantity
        )

    def test_destroy_sell_without_group_does_not_break(self):
        """Una venta sin grupo se borra sin intentar anotar nada."""
        sell = baker.make(
            Sell,
            sell_group=None,
            shop_product=baker.make(
                ShopProducts, cost_price=1, sell_price=Decimal("10.00"), quantity=50
            ),
            quantity=2,
        )
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        url = reverse("sell-products-detail", kwargs={"pk": sell.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Sell.objects.filter(id=sell.id).exists())
