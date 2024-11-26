import pytest
from django.urls import reverse

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.tests import sells, shop_products
from apps.business_app.views import shop
from apps.common.baseclass_for_testing import BaseTestClass
from apps.users_app.models.groups import Groups
from model_bakery import baker

from rest_framework import status


@pytest.mark.django_db
class TestDashboardViewSetFunctionalities(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_authenticate(self.user)

    def test_shop_product_investment(self):
        test_shop1 = baker.make(Shop)
        test_shop2 = baker.make(Shop)
        random_qty_for_test_shop1 = baker.random_gen.gen_integer(min_int=1, max_int=10)
        random_qty_for_test_shop2 = baker.random_gen.gen_integer(min_int=1, max_int=10)
        random_equal_cost = baker.random_gen.gen_integer(min_int=10, max_int=20)

        baker.make(
            ShopProducts,
            shop=test_shop1,
            cost_price=random_equal_cost,
            quantity=1,
            _quantity=random_qty_for_test_shop1,
        )
        baker.make(
            ShopProducts,
            shop=test_shop2,
            cost_price=random_equal_cost,
            quantity=1,
            _quantity=random_qty_for_test_shop1,
        )

        url = reverse("dashboard-shop-product-investment")
        self.client.post(url, format="json")
