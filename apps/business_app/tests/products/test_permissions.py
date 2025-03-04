import pytest
from django.urls import reverse

from apps.business_app.models.product import Product
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.users_app.models.groups import Groups
from model_bakery import baker



@pytest.mark.django_db
class TestProductsViewSet(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()
        self.allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER]

    def test_get_protocol(self):
        """
        Solo el SUPER_ADMIN y el SHOP_OWNER pueden ver datos
        """
        url = reverse("products-list")

        self._test_permissions(
            url,
            allowed_roles=self.allowed_groups,
            request_using_protocol=self.client.get,
        )
        test_product = baker.make(
            Product,
        )
        url = reverse("products-detail", kwargs={"pk": test_product.id})

        self._test_permissions(
            url,
            allowed_roles=self.allowed_groups,
            request_using_protocol=self.client.get,
        )

    def test_post_protocol(self):
        """
        Solo el SUPER_ADMIN y el SHOP_OWNER pueden introducir datos
        """
        url = reverse("products-list")

        self._test_permissions(
            url,
            allowed_roles=self.allowed_groups,
            request_using_protocol=self.client.post,
        )

    def test_put_patch_delete_protocols(self):
        """
        Solo el SUPER_ADMIN y el SHOP_OWNER pueden cambiar datos
        """
        test_product = baker.make(
            ShopProducts,
            cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
            sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
        )
        url = reverse("products-detail", kwargs={"pk": test_product.id})
        test_protocols = [self.client.put, self.client.patch, self.client.delete]
        for protocol in test_protocols:
            self._test_permissions(
                url, allowed_roles=self.allowed_groups, request_using_protocol=protocol
            )
