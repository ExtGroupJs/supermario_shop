
from datetime import datetime, timedelta
import datetime
import pytest
from django.urls import reverse
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.users_app.models.groups import Groups
from model_bakery import baker
from rest_framework import status

from freezegun import freeze_time



@pytest.mark.django_db
class TestShopProductsViewSet(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()

    @freeze_time(datetime.datetime.now() - timedelta(days=40))
    def test_is_new_is_in_response_and_is_false_since_has_more_than_one_month(self):
        """
        Se puede acceder con cualquier rol, siempre y cuando sea un usuario registrado
        """
        test_shop_product = baker.make(
            ShopProducts,
            cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
            sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
        )
        url = reverse("shop-products-detail", kwargs={"pk": test_shop_product.id})
        self.client.force_authenticate(user=self.user)
        self.user.groups.add(Groups.SHOP_OWNER)
        
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("is_new", response.data.keys())
        self.assertFalse(response.data.get("is_new"))


    @freeze_time(datetime.datetime.now() - timedelta(days=29))
    def test_is_new_is_in_response_and_is_true_since_has_less_than_one_month(self):
        """
        Se puede acceder con cualquier rol, siempre y cuando sea un usuario registrado
        """
        test_shop_product = baker.make(
            ShopProducts,
            cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
            sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
        )
        url = reverse("shop-products-detail", kwargs={"pk": test_shop_product.id})
        self.client.force_authenticate(user=self.user)
        self.user.groups.add(Groups.SHOP_OWNER)
        
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("is_new", response.data.keys())
        self.assertTrue(response.data.get("is_new"))
