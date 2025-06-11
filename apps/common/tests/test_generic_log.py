import pytest
from model_bakery import baker
from django.contrib.contenttypes.models import ContentType
from apps.business_app.models.shop_products import ShopProducts
from apps.common.baseclass_for_testing import BaseTestClass
from apps.common.models.generic_log import GenericLog


@pytest.mark.django_db
class TestSellGroupsViewSetFunctionalities(BaseTestClass):
    def setUp(self):
        super().setUp()
        self.maxDiff = None

        self.created_instance = baker.make(ShopProducts, cost_price=1, sell_price=2)

    def test_create_log_entry_on_save(self):
        log_entry = GenericLog.objects.get(object_id=self.created_instance.pk)
        self.assertEqual(log_entry.performed_action, GenericLog.ACTION.CREATED)
        self.assertEqual(
            log_entry.content_type, ContentType.objects.get_for_model(ShopProducts)
        )
        expected_details = {
            "shop": {"new_value": f"{self.created_instance.shop}", "old_value": None},
            "product": {
                "new_value": f"{self.created_instance.product}",
                "old_value": None,
            },
            "cost_price": {
                "new_value": self.created_instance.cost_price,
                "old_value": None,
            },
            "sell_price": {
                "new_value": self.created_instance.sell_price,
                "old_value": None,
            },
        }

        self.assertEqual(log_entry.details, expected_details)

    def test_update_log_entry_on_save(self):
        old_price = self.created_instance.sell_price
        new_price = baker.random_gen.gen_integer(old_price + 1, old_price + 10)
        self.created_instance.sell_price = new_price
        self.created_instance.save()
        log_entry = GenericLog.objects.filter(object_id=self.created_instance.pk).last()
        self.assertEqual(log_entry.performed_action, GenericLog.ACTION.UPDATED)
        self.assertEqual(
            log_entry.content_type, ContentType.objects.get_for_model(ShopProducts)
        )
        key_to_check = "sell_price"
        self.assertTrue(key_to_check in log_entry.details)
        details = log_entry.details
        self.assertEqual(details[key_to_check]["old_value"], old_price)
        self.assertEqual(details[key_to_check]["new_value"], new_price)

    def test_update_log_entry_sell_price_is_logged_as_float(self):
        old_price = self.created_instance.sell_price
        new_price = baker.random_gen.gen_integer(old_price + 1, old_price + 10)
        self.created_instance.sell_price = new_price
        self.created_instance.save()
        log_entry = GenericLog.objects.filter(object_id=self.created_instance.pk).last()
        self.assertEqual(log_entry.performed_action, GenericLog.ACTION.UPDATED)
        self.assertEqual(
            log_entry.content_type, ContentType.objects.get_for_model(ShopProducts)
        )
        key_to_check = "sell_price"
        self.assertTrue(key_to_check in log_entry.details)
        details = log_entry.details
        self.assertEqual(details[key_to_check]["old_value"], old_price)
        self.assertEqual(details[key_to_check]["new_value"], new_price)

        self.assertTrue(isinstance(details[key_to_check]["old_value"], float))
        self.assertTrue(isinstance(details[key_to_check]["new_value"], float))

    def test_update_log_entry_cost_price_is_logged_as_float(self):
        old_price = self.created_instance.cost_price
        new_price = old_price - 0.5
        self.created_instance.cost_price = new_price
        self.created_instance.save()
        log_entry = GenericLog.objects.filter(object_id=self.created_instance.pk).last()
        self.assertEqual(log_entry.performed_action, GenericLog.ACTION.UPDATED)
        self.assertEqual(
            log_entry.content_type, ContentType.objects.get_for_model(ShopProducts)
        )
        key_to_check = "cost_price"
        self.assertTrue(key_to_check in log_entry.details)
        details = log_entry.details
        self.assertEqual(details[key_to_check]["old_value"], old_price)
        self.assertEqual(details[key_to_check]["new_value"], new_price)

        self.assertTrue(isinstance(details[key_to_check]["old_value"], float))
        self.assertTrue(isinstance(details[key_to_check]["new_value"], float))

    def test_update_log_entry_quantity_is_logged_as_int(self):
        old_quantity = self.created_instance.quantity
        new_quantity = baker.random_gen.gen_integer(old_quantity + 1, old_quantity + 10)
        self.created_instance.quantity = new_quantity
        self.created_instance.save()
        log_entry = GenericLog.objects.filter(object_id=self.created_instance.pk).last()
        self.assertEqual(log_entry.performed_action, GenericLog.ACTION.UPDATED)
        self.assertEqual(
            log_entry.content_type, ContentType.objects.get_for_model(ShopProducts)
        )
        key_to_check = "quantity"
        self.assertTrue(key_to_check in log_entry.details)
        details = log_entry.details
        self.assertEqual(details[key_to_check]["old_value"], old_quantity)
        self.assertEqual(details[key_to_check]["new_value"], new_quantity)

        self.assertTrue(isinstance(details[key_to_check]["old_value"], int))
        self.assertTrue(isinstance(details[key_to_check]["new_value"], int))

    def test_delete_log_entry(self):
        self.created_instance.delete()
        log_entry = GenericLog.objects.filter(object_id=self.created_instance.pk).last()
        self.assertEqual(log_entry.performed_action, GenericLog.ACTION.DELETED)
        self.assertEqual(
            log_entry.content_type, ContentType.objects.get_for_model(ShopProducts)
        )

    def test_no_log_entry_on_no_change(self):
        self.created_instance.save()
        log_entries = GenericLog.objects.filter(object_id=self.created_instance.pk)
        self.assertEqual(
            log_entries.count(), 1
        )  # Only the creation log entry should exist
