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
class TestGroupSellViewSetFunctionalities(BaseTestClass):
    fixtures = ["auth.group.json"]

    def _make_sale(self, **group_kwargs):
        """A sell group with one sell in it, the smallest sale the listing can show."""
        client = group_kwargs.pop("client", None)
        group_kwargs.setdefault("total", Decimal("30.00"))
        group_kwargs.setdefault("discount", 0)
        sell_group = baker.make(SellGroup, client=client, **group_kwargs)
        sell = baker.make(
            Sell,
            sell_group=sell_group,
            shop_product=baker.make(
                ShopProducts,
                cost_price=Decimal("4.00"),
                sell_price=Decimal("10.00"),
                quantity=20,
            ),
            quantity=3,
        )
        return sell_group, sell

    def _payload(self, response, group_id):
        return next(item for item in response.json()["results"] if item["id"] == group_id)

    def test_get_protocol(self):
        """Se puede acceder con cualquier rol, siempre y cuando sea un usuario registrado"""
        url = reverse("group-sells-list")
        allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER, Groups.SHOP_SELLER]

        self._test_permissions(
            url, allowed_roles=allowed_groups, request_using_protocol=self.client.get
        )

    def test_get_one_protocol(self):
        """El detalle de un grupo se puede leer con cualquier rol registrado"""
        sell_group, _ = self._make_sale()
        url = reverse("group-sells-detail", args=[sell_group.id])
        allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER, Groups.SHOP_SELLER]

        self._test_permissions(
            url, allowed_roles=allowed_groups, request_using_protocol=self.client.get
        )

    def test_group_row_carries_the_sale_and_nests_its_sells(self):
        """
        Cada fila es un grupo de venta con sus datos y las ventas anidadas debajo,
        en vez de una venta por fila.
        """
        client = baker.make(Client, name="Cliente Anidado", phone="5842222222")
        sell_group, sell = self._make_sale(client=client)
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        response = self.client.get(reverse("group-sells-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        group = self._payload(response, sell_group.id)
        self.assertEqual(group["client_name"], "Cliente Anidado")
        self.assertEqual(group["client_phone"], "5842222222")
        self.assertEqual(Decimal(str(group["total"])), Decimal("30.00"))
        self.assertEqual(group["sells_count"], 1)
        self.assertEqual(len(group["sells"]), 1)

        line = group["sells"][0]
        self.assertEqual(line["id"], sell.id)
        self.assertEqual(line["quantity"], 3)
        self.assertEqual(Decimal(str(line["sell_price"])), Decimal("10.00"))
        self.assertEqual(Decimal(str(line["total_priced"])), Decimal("30.00"))

    def test_nested_sells_resolve_the_product_name_and_the_profit(self):
        """
        Las ventas anidadas llegan con producto y ganancia.

        Es el punto delicate del endpoint: esos datos no son columnas de ``Sell``,
        solo existen como anotaciones, asi que sin el prefetch con ellas el producto
        y el precio de la fila hija saldrian vacios.
        """
        shop_product = baker.make(
            ShopProducts,
            cost_price=Decimal("4.00"),
            sell_price=Decimal("10.00"),
            quantity=20,
        )
        sell_group = baker.make(SellGroup, total=Decimal("20.00"))
        baker.make(Sell, sell_group=sell_group, shop_product=shop_product, quantity=2)
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        response = self.client.get(reverse("group-sells-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        line = self._payload(response, sell_group.id)["sells"][0]
        self.assertIn(shop_product.product.name, line["product_name"])
        # Ganancia: (10.00 - 4.00) * 2
        self.assertEqual(Decimal(str(line["profits"])), Decimal("12.00"))

    def test_nested_sell_carries_no_repeated_group_data(self):
        """
        La venta anidada no repite los datos del grupo.

        El cliente, el total, el descuento y la nota ya viajan en la fila del grupo,
        asi que repetirlos en cada venta solo agranda la respuesta.
        """
        sell_group, _ = self._make_sale(client=baker.make(Client, name="Cliente"))
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        response = self.client.get(reverse("group-sells-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        line = self._payload(response, sell_group.id)["sells"][0]
        for group_only_field in ("client_name", "group_total", "discounts"):
            self.assertNotIn(group_only_field, line)

    def test_net_total_is_the_group_total_minus_the_discount(self):
        """El importe neto es el total del grupo menos su descuento"""
        sell_group, _ = self._make_sale(total=Decimal("30.00"), discount=5)
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        response = self.client.get(reverse("group-sells-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            Decimal(str(self._payload(response, sell_group.id)["net_total"])),
            Decimal("25.00"),
        )

    def test_net_total_never_goes_below_zero(self):
        """Un descuento mayor que el total deja el importe neto en cero, no en negativo"""
        sell_group, _ = self._make_sale(total=Decimal("10.00"), discount=25)
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        response = self.client.get(reverse("group-sells-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            Decimal(str(self._payload(response, sell_group.id)["net_total"])),
            Decimal("0.00"),
        )

    def test_group_row_shows_the_date_the_seller_gave_the_sale(self):
        """
        La fila del grupo muestra el ``for_date`` del grupo, no la fecha de creacion
        de una de sus ventas.
        """
        sell_group, _ = self._make_sale()
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        response = self.client.get(reverse("group-sells-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        group = self._payload(response, sell_group.id)
        self.assertEqual(
            group["for_date_label"],
            sell_group.for_date.strftime("%d-%b-%Y %I:%M %p"),
        )

    def test_listing_can_be_filtered_by_period(self):
        """Las ventas se filtran por el periodo del ``for_date`` del grupo"""
        old_group, _ = self._make_sale()
        old_group.for_date = old_group.for_date.replace(year=2001)
        old_group.save()
        new_group, _ = self._make_sale()
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("group-sells-list"),
            {"for_date__date__gte": new_group.for_date.strftime("%Y-%m-%d")},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        listed_ids = [item["id"] for item in response.json()["results"]]
        self.assertIn(new_group.id, listed_ids)
        self.assertNotIn(old_group.id, listed_ids)

    def test_listing_can_be_sorted_by_net_total(self):
        """
        El importe neto se puede ordenar.

        Es una columna calculada, asi que el queryset la anota para que el orden
        exista en la base de datos.
        """
        cheap_group, _ = self._make_sale(total=Decimal("10.00"), discount=0)
        rich_group, _ = self._make_sale(total=Decimal("90.00"), discount=0)
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("group-sells-list"), {"ordering": "-net_total"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        listed_ids = [item["id"] for item in response.json()["results"]]
        self.assertLess(listed_ids.index(rich_group.id), listed_ids.index(cheap_group.id))

    def test_seller_only_sees_the_sales_of_its_own_shop(self):
        """Un vendedor solo ve los grupos de su propia tienda"""
        own_shop_product = baker.make(
            ShopProducts, shop=self.user.shop, sell_price=Decimal("10.00"), quantity=20
        )
        own_group = baker.make(SellGroup, total=Decimal("20.00"))
        baker.make(
            Sell, sell_group=own_group, shop_product=own_shop_product, quantity=2
        )
        other_shop_product = baker.make(
            ShopProducts,
            shop=baker.make("business_app.Shop"),
            sell_price=Decimal("10.00"),
            quantity=20,
        )
        other_group = baker.make(SellGroup, total=Decimal("20.00"))
        baker.make(
            Sell, sell_group=other_group, shop_product=other_shop_product, quantity=2
        )

        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)

        response = self.client.get(reverse("group-sells-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        listed_ids = [item["id"] for item in response.json()["results"]]
        self.assertIn(own_group.id, listed_ids)
        self.assertNotIn(other_group.id, listed_ids)

    def test_seller_cannot_read_another_shop_sale_by_detail(self):
        """Un vendedor no puede abrir el detalle de un grupo de otra tienda"""
        other_shop_product = baker.make(
            ShopProducts,
            shop=baker.make("business_app.Shop"),
            sell_price=Decimal("10.00"),
            quantity=20,
        )
        other_group = baker.make(SellGroup, total=Decimal("20.00"))
        baker.make(
            Sell, sell_group=other_group, shop_product=other_shop_product, quantity=2
        )
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("group-sells-detail", args=[other_group.id])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_seller_sees_its_own_shop_product_name_without_the_shop_suffix(self):
        """
        El vendedor ve el producto sin el nombre de la tienda.

        Ya solo ve su tienda, asi que el nombre de la tienda al final del producto
        solo ocuparia espacio en su pantalla.
        """
        shop_product = baker.make(
            ShopProducts, shop=self.user.shop, sell_price=Decimal("10.00"), quantity=20
        )
        sell_group = baker.make(SellGroup, total=Decimal("20.00"))
        baker.make(Sell, sell_group=sell_group, shop_product=shop_product, quantity=2)
        self.user.groups.add(Groups.SHOP_SELLER)
        self.client.force_login(self.user)

        response = self.client.get(reverse("group-sells-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        line = self._payload(response, sell_group.id)["sells"][0]
        self.assertIn(shop_product.product.name, line["product_name"])
        self.assertNotIn(shop_product.shop.name, line["product_name"])

    def test_group_without_client_is_listed_with_an_empty_client(self):
        """
        Un grupo sin cliente se lista igual, con el cliente vacio.

        La venta en mostrador no tiene cliente, y el filtro por cliente no puede
        dejar fuera esas ventas de la pantalla.
        """
        sell_group, _ = self._make_sale(client=None)
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_login(self.user)

        response = self.client.get(reverse("group-sells-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        group = self._payload(response, sell_group.id)
        self.assertEqual(group["client_name"], "")
        self.assertEqual(group["sells_count"], 1)
