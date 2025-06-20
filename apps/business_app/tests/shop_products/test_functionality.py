from datetime import datetime, timedelta
import pytest
from django.urls import reverse
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.common.models.generic_log import GenericLog
from apps.users_app.models.groups import Groups
from model_bakery import baker
from rest_framework import status

from freezegun import freeze_time



@pytest.mark.django_db
class TestShopProductsViewSet(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()

    @freeze_time(datetime.now() - timedelta(days=40))
    def test_is_new_is_in_catalog_response_and_is_false_since_has_more_than_one_month(
        self,
    ):
        """
        Se puede acceder con cualquier rol, siempre y cuando sea un usuario registrado
        """
        with freeze_time(datetime.now() - timedelta(days=40)):
            baker.make(
                ShopProducts,
                cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
                sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
            )
        url = reverse("shop-products-catalog")
        self.client.force_authenticate(user=self.user)
        self.user.groups.add(Groups.SHOP_OWNER)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        retreived_object = response.data["results"][0]
        self.assertIn("is_new", retreived_object.keys())
        self.assertFalse(retreived_object.get("is_new"))

    def test_is_new_is_in_catalog_response_and_is_true_since_has_less_than_one_month(
        self,
    ):
        """
        Se puede acceder con cualquier rol, siempre y cuando sea un usuario registrado
        """
        with freeze_time(datetime.now() - timedelta(days=29)):
            baker.make(
                ShopProducts,
                cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
                sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
            )
        url = reverse("shop-products-catalog")
        self.client.force_authenticate(user=self.user)
        self.user.groups.add(Groups.SHOP_OWNER)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        retreived_object = response.data["results"][0]

        self.assertIn("is_new", retreived_object.keys())
        self.assertTrue(retreived_object.get("is_new"))

    @freeze_time(datetime.now() - timedelta(days=40))
    def test_is_new_is_in_catalog_response_and_is_false_since_has_more_than_one_month_with_anonimous_caller(
        self,
    ):
        """ """
        with freeze_time(datetime.now() - timedelta(days=40)):
            baker.make(
                ShopProducts,
                cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
                sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
                quantity=baker.random_gen.gen_integer(min_int=1, max_int=10),
            )
        url = reverse("shop-products-catalog")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        retreived_object = response.data["results"][0]
        self.assertIn("is_new", retreived_object.keys())
        self.assertFalse(retreived_object.get("is_new"))

    def test_is_new_is_in_catalog_response_and_is_true_since_has_less_than_one_month_with_anonimous_caller(
        self,
    ):
        """
        Prueba que se puede acceder al catálogo sin estar registrado
        """
        with freeze_time(datetime.now() - timedelta(days=29)):
            baker.make(
                ShopProducts,
                cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
                sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
                quantity=baker.random_gen.gen_integer(min_int=1, max_int=10),
            )
        url = reverse("shop-products-catalog")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        retreived_object = response.data["results"][0]

        self.assertIn("is_new", retreived_object.keys())
        self.assertTrue(retreived_object.get("is_new"))

    def test_shop_products_logs_filters(
        self,
    ):
        """
        Prueba que se puede acceder al catálogo sin estar registrado
        """
        self.client.force_authenticate(user=self.user)
        # self.user.groups.add(Groups.SHOP_OWNER)
        # GenericLog.objects.all().delete()

        shop_product = baker.make(
            ShopProducts,
            cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
            sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
            quantity=baker.random_gen.gen_integer(min_int=1, max_int=10),
        )

        incomings = baker.random_gen.gen_integer(6, 10)
        sells = baker.random_gen.gen_integer(1, 5)

        for _ in range(incomings):
            shop_product.quantity = shop_product.quantity + 1
            shop_product.save(update_fields=["quantity"])

        for _ in range(sells):
            shop_product.quantity = shop_product.quantity - 1
            shop_product.save(update_fields=["quantity"])

        url = reverse("shop-products-logs-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(
            response_data["count"], sells + incomings + 1
        )  # without params all logs are retrieved

        response = self.client.get(f"{url}?entries=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(
            response_data["count"], incomings + 1
        )  # only incrementations in quantity are retrieved

        response = self.client.get(f"{url}?entries=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(
            response_data["count"], sells
        )  # only decrementations in quantity are retrieved

    def test_shop_products_logs_generated_only_for_non_deleted_shop_products(
        self,
    ):
        """ """
        self.client.force_authenticate(user=self.user)

        shop_product = baker.make(
            ShopProducts,
            cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
            sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
            quantity=baker.random_gen.gen_integer(min_int=1, max_int=10),
        )

        url = reverse("shop-products-logs-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(
            response_data["count"], 1
        )  # without params all logs are retrieved

        shop_product.delete()

        # if shop_product is deleted, the log is not shown despite it exists on db
        self.assertEqual(
            GenericLog.objects.count(), 2
        )  # an additional one due to the deletion
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], None)
