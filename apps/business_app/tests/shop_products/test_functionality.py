from datetime import datetime, timedelta
import pytest
from django.urls import reverse
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.shop_products import MoveToAnotherShopSerializer
from apps.common.baseclass_for_testing import BaseTestClass
from apps.common.models.generic_log import GenericLog
from apps.common.models.generic_log import GenericLog
from apps.users_app.models.groups import Groups
from model_bakery import baker
from rest_framework import status

from freezegun import freeze_time

from apps.users_app.models.system_user import SystemUser

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

    def test_move_to_another_shop_validations(self):
        """ """

        random_quantity = baker.random_gen.gen_integer(min_int=2, max_int=10)
        test_shop_product = baker.make(
            ShopProducts,
            cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
            sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
            quantity=random_quantity,
        )
        url = reverse(
            "shop-products-move-to-another-shop", kwargs={"pk": test_shop_product.id}
        )
        destiny_shop = baker.make(Shop)

        self.client.force_authenticate(user=self.user)
        self.user.groups.add(Groups.SHOP_OWNER)

        failing_key = "quantity"
        # Testing quantity=0 is not allowed to be moved
        payload = {
            "shop": destiny_shop.id,
            failing_key: 0,
        }

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.json()[failing_key][0],
            MoveToAnotherShopSerializer.default_error_messages.get(
                "quantity_lesser_than_one"
            ),
        )

        # Testing quantity should not be greater han available quantity on shop_product instance
        payload = {
            "shop": destiny_shop.id,
            failing_key: test_shop_product.quantity + 1,
        }

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.json()[failing_key][0],
            MoveToAnotherShopSerializer.default_error_messages.get(
                "quantity_greater_than_available"
            ),
        )

        failing_key = "shop"
        random_quantity_to_move = baker.random_gen.gen_integer(
            min_int=1, max_int=test_shop_product.quantity
        )
        # Testing shop was not provided
        payload = {
            failing_key: test_shop_product.shop.id,
            "quantity": random_quantity_to_move,
        }

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.json()[failing_key][0],
            MoveToAnotherShopSerializer.default_error_messages.get(
                "destiny_shop_must_be_diferent"
            ),
        )

    def test_move_to_another_shop_logic(self):
        """ """

        random_quantity = baker.random_gen.gen_integer(min_int=3, max_int=10)
        test_shop_product = baker.make(
            ShopProducts,
            cost_price=baker.random_gen.gen_integer(min_int=1, max_int=2),
            sell_price=baker.random_gen.gen_integer(min_int=3, max_int=5),
            quantity=random_quantity,
        )
        url = reverse(
            "shop-products-move-to-another-shop", kwargs={"pk": test_shop_product.id}
        )
        destiny_shop = baker.make(Shop)

        self.client.force_authenticate(user=self.user)
        self.user.groups.add(Groups.SHOP_OWNER)

        random_quantity_to_move = baker.random_gen.gen_integer(
            min_int=2, max_int=test_shop_product.quantity
        )

        payload = {
            "shop": destiny_shop.id,
            "quantity": random_quantity_to_move,
        }
        same_shop_product_in_new_shop = ShopProducts.objects.filter(
            shop=destiny_shop, product=test_shop_product.product
        ).first()

        # Should not exist
        self.assertIsNone(
            same_shop_product_in_new_shop,
        )

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        same_shop_product_in_new_shop = ShopProducts.objects.filter(
            shop=destiny_shop, product=test_shop_product.product
        ).first()

        # Testing new shop product was created for destiny shop with correct quantity and same atributes thahn original one!!!
        self.assertIsNotNone(same_shop_product_in_new_shop)
        self.assertEqual(
            test_shop_product.cost_price, same_shop_product_in_new_shop.cost_price
        )
        self.assertEqual(
            test_shop_product.sell_price, same_shop_product_in_new_shop.sell_price
        )
        self.assertEqual(
            test_shop_product.product, same_shop_product_in_new_shop.product
        )
        self.assertEqual(
            test_shop_product.extra_info, same_shop_product_in_new_shop.extra_info
        )
        self.assertNotEqual(test_shop_product.shop, same_shop_product_in_new_shop.shop)

        self.assertEqual(
            GenericLog.objects.filter(
                object_id=test_shop_product.id, extra_log_info__isnull=False
            ).count(),
            1,
        )
        self.assertEqual(
            GenericLog.objects.filter(
                object_id=same_shop_product_in_new_shop.id, extra_log_info__isnull=False
            ).count(),
            1,
        )

        # Testing the correct amount was substracted from original shop product and assigned to destiny one
        test_shop_product.refresh_from_db()
        self.assertEqual(
            test_shop_product.quantity, random_quantity - payload["quantity"]
        )
        self.assertEqual(same_shop_product_in_new_shop.quantity, payload["quantity"])

        first_payload_qty = payload["quantity"]
        random_quantity_to_move = baker.random_gen.gen_integer(
            min_int=1, max_int=test_shop_product.quantity
        )

        payload = {
            "shop": destiny_shop.id,
            "quantity": random_quantity_to_move,
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        before_qty = test_shop_product.quantity
        test_shop_product.refresh_from_db()
        self.assertEqual(test_shop_product.quantity, before_qty - payload["quantity"])
        same_shop_product_in_new_shop.refresh_from_db()
        self.assertEqual(
            same_shop_product_in_new_shop.quantity,
            first_payload_qty + payload["quantity"],
        )

        self.assertEqual(
            GenericLog.objects.filter(
                object_id=test_shop_product.id, extra_log_info__isnull=False
            ).count(),
            2,
        )
        self.assertEqual(
            GenericLog.objects.filter(
                object_id=same_shop_product_in_new_shop.id, extra_log_info__isnull=False
            ).count(),
            2,
        )
