import pytest
from django.urls import reverse

from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.users_app.models.groups import Groups
from model_bakery import baker

from rest_framework import status


@pytest.mark.django_db
class TestProductViewSetFunctionalities(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()
        self.user.groups.add(Groups.SHOP_OWNER)
        self.client.force_authenticate(self.user)

    def test_product_insertion(self):
        payload = {
            "name": baker.random_gen.gen_string(10),
            "model": baker.make("business_app.Model").id,
            "description": baker.random_gen.gen_string(50),
            "image": None,
        }
        url = reverse("products-list")
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], payload["name"])
        self.assertEqual(response.data["model"], payload["model"])
        self.assertEqual(response.data["description"], payload["description"])
        self.assertEqual(response.data["image"], None)

    def test_product_unique_together_restriction(self):
        payload = {
            "name": baker.random_gen.gen_string(10),
            "model": baker.make("business_app.Model").id,
            "description": baker.random_gen.gen_string(50),
            "image": None,
        }
        url = reverse("products-list")
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )  # first call insert the product ok
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Los campos name, model deben formar un conjunto único.",
            response.data["non_field_errors"],
        )
