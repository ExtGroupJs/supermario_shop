from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.business_app.models.sell import Sell


def update_inventory(inc_pos_dec_neg, instance):
    """
    The increment only defines the operation, if is -1 the value is decremented, if +1, incremented
    """
    shop_product = instance.shop_product
    shop_product.quantity += inc_pos_dec_neg * instance.quantity
    shop_product.save(update_fields=["quantity"])


@receiver(post_save, sender=Sell)
def remove_from_inventory(sender, instance, **kwargs):
    update_inventory(inc_pos_dec_neg=-1, instance=instance)


@receiver(post_delete, sender=Sell)
def restored_inventory(sender, instance, **kwargs):
    update_inventory(inc_pos_dec_neg=1, instance=instance)
