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
        self.created_instance = baker.make(ShopProducts, cost_price=1, sell_price=2)

    def test_create_log_entry_on_save(self):
        log_entry = GenericLog.objects.get(object_id=self.created_instance.pk)
        self.assertEqual(log_entry.performed_action, GenericLog.ACTION.CREATED)
        self.assertEqual(
            log_entry.content_type, ContentType.objects.get_for_model(ShopProducts)
        )
        expected_details = {
            "shop": {"old_value": None, "new_value": f"{self.created_instance.shop}"},
            "product": {
                "old_value": None,
                "new_value": f"{self.created_instance.product}",
            },
            "cost_price": {
                "old_value": None,
                "new_value": f"{self.created_instance.cost_price}",
            },
            "sell_price": {
                "old_value": None,
                "new_value": f"{self.created_instance.sell_price}",
            },
        }
        self.assertEqual(log_entry.details, expected_details)

    def test_update_log_entry_on_save(self):
        self.created_instance.sell_price = 3
        self.created_instance.save()
        log_entry = GenericLog.objects.filter(object_id=self.created_instance.pk).last()
        self.assertEqual(log_entry.performed_action, GenericLog.ACTION.UPDATED)
        self.assertEqual(
            log_entry.content_type, ContentType.objects.get_for_model(ShopProducts)
        )
        self.assertTrue("sell_price" in log_entry.details)
        details = log_entry.details
        self.assertEqual(details["sell_price"]["old_value"], "2.00")
        self.assertEqual(details["sell_price"]["new_value"], "3")

    def test_delete_log_entry(self):
        self.created_instance.delete()
        log_entry = GenericLog.objects.filter(object_id=self.created_instance.pk).last()
        self.assertEqual(log_entry.performed_action, GenericLog.ACTION.DELETED)
        self.assertEqual(
            log_entry.content_type, ContentType.objects.get_for_model(ShopProducts)
        )

    @pytest.mark.django_db
    def test_no_log_entry_on_no_change(self):
        self.created_instance.save()
        log_entries = GenericLog.objects.filter(object_id=self.created_instance.pk)
        self.assertEqual(
            log_entries.count(), 1
        )  # Only the creation log entry should exist
