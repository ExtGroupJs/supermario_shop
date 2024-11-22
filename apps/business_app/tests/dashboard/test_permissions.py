import pytest
from django.urls import reverse

from apps.common.baseclass_for_testing import BaseTestClass
from apps.users_app.models.groups import Groups


@pytest.mark.django_db
class TestDashboardViewSet(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()
        self.allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER]

    def test_shop_product_investment_permissions(self):
        """
        Este test comprueba que solo un superadmin o un SHOP_OWNER pueden acceder a la funcionalidad
        """
        url = reverse("dashboard-shop-product-investment")
        self._test_permissions(
            url,
            allowed_roles=self.allowed_groups,
            request_using_protocol=self.client.post,
        )

    def test_sell_profits_permissions(self):
        """
        Este test comprueba que solo un superadmin o un SHOP_OWNER pueden acceder a la funcionalidad
        """
        url = reverse("dashboard-sell-profits")
        self._test_permissions(
            url,
            allowed_roles=self.allowed_groups,
            request_using_protocol=self.client.post,
        )

    def test_shop_product_sell_count_permissions(self):
        """
        Este test comprueba que solo un superadmin o un SHOP_OWNER pueden acceder a la funcionalidad
        """
        url = reverse("dashboard-shop-product-sell-count")
        self._test_permissions(
            url,
            allowed_roles=self.allowed_groups,
            request_using_protocol=self.client.post,
        )

    def test_shop_product_sell_products_count_permissions(self):
        """
        Este test comprueba que solo un superadmin o un SHOP_OWNER pueden acceder a la funcionalidad
        """
        url = reverse("dashboard-shop-product-sell-products-count")
        self._test_permissions(
            url,
            allowed_roles=self.allowed_groups,
            request_using_protocol=self.client.post,
        )
