import pytest
from django.urls import reverse

from apps.business_app.models.sell import Sell
from apps.business_app.models.shop_products import ShopProducts
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
