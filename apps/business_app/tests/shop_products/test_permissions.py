import pytest
from django.urls import reverse

from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.users_app.models.groups import Groups
from model_bakery import baker


@pytest.mark.django_db
class TestShopProductsViewSet(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()

    def test_get_protocol(self):
        """
        Se puede acceder con cualquier rol, siempre y cuando sea un usuario registrado
        """
        url = reverse("shop-products-list")
        allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER, Groups.SHOP_SELLER]

        self._test_permissions(
            url, allowed_roles=allowed_groups, request_using_protocol=self.client.get
        )

    def test_get_one_protocol(self):
        """
        Se puede acceder con cualquier rol, siempre y cuando sea un usuario registrado
        """
        test_shop_product = baker.make(
            ShopProducts,
            cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
            sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
        )
        url = reverse("shop-products-detail", kwargs={"pk": test_shop_product.id})
        allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER, Groups.SHOP_SELLER]

        self._test_permissions(
            url, allowed_roles=allowed_groups, request_using_protocol=self.client.get
        )

    def test_post_protocol(self):
        """
        Solo el SUPER_ADMIN y el SHOP_OWNER pueden introducir datos
        """
        url = reverse("shop-products-list")
        allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER]

        self._test_permissions(
            url, allowed_roles=allowed_groups, request_using_protocol=self.client.post
        )

    def test_put_patch_delete_protocols(self):
        """
        Solo el SUPER_ADMIN y el SHOP_OWNER pueden cambiar datos
        """
        test_shop_product = baker.make(
            ShopProducts,
            cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
            sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
        )
        url = reverse("shop-products-detail", kwargs={"pk": test_shop_product.id})
        allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER]
        test_protocols = [self.client.put, self.client.patch, self.client.delete]
        for protocol in test_protocols:
            self._test_permissions(
                url, allowed_roles=allowed_groups, request_using_protocol=protocol
            )
