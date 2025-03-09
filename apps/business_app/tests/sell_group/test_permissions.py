import pytest
from django.urls import reverse

from apps.common.baseclass_for_testing import BaseTestClass
from apps.users_app.models.groups import Groups


@pytest.mark.django_db
class TestSellGroupsViewSetPermissions(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()

    def test_get_protocol(self):
        """
        Se puede acceder con cualquier rol, siempre y cuando sea un usuario registrado
        """
        url = reverse("sell-groups-list")
        allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER, Groups.SHOP_SELLER]

        self._test_permissions(
            url, allowed_roles=allowed_groups, request_using_protocol=self.client.get
        )

    # TODO implementar
    # def test_get_one_protocol(self):
    #     """
    #     Se puede acceder con cualquier rol, siempre y cuando sea un usuario registrado
    #     """
    #     test_sell = baker.make(
    #         SellGroup,

    #         quantity=baker.random_gen.gen_integer(min_int=1, max_int=2),
    #     )
    #     url = reverse("sell-groups-detail", kwargs={"pk": test_sell.id})
    #     allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER, Groups.SHOP_SELLER]

    #     self._test_permissions(
    #         url, allowed_roles=allowed_groups, request_using_protocol=self.client.get
    #     )

    def test_post_protocol(self):
        """
        Solo el SUPER_ADMIN y el SHOP_OWNER pueden introducir datos
        """
        url = reverse("sell-groups-list")
        allowed_groups = [Groups.SUPER_ADMIN, Groups.SHOP_OWNER, Groups.SHOP_SELLER]

        self._test_permissions(
            url, allowed_roles=allowed_groups, request_using_protocol=self.client.post
        )
