from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.business_app.models.sell import Sell
from apps.business_app.models.shop_product_input_model import ShopProductInput
from apps.business_app.models.shop_products import ShopProducts


def update_inventory(inc_pos_dec_neg, instance):
    """
    The increment only defines the operation, if is -1 the value is decremented, if +1, incremented
    """
    shop_product = ShopProducts.objects.filter(id=instance.shop_product.id).first()
    if shop_product:
        shop_product.quantity += inc_pos_dec_neg * instance.quantity
        extra_log_info = None
        if isinstance(instance, ShopProductInput):
            extra = ""
            if inc_pos_dec_neg == -1:
                extra = " cancelada"
            extra_log_info = f"Entrada del {instance.shop_product_input_group.for_date.strftime('%d-%h-%Y')}{extra}"
        shop_product.save(update_fields=["quantity"], extra_log_info=extra_log_info)


@receiver(post_save, sender=Sell)
def remove_from_inventory(sender, instance, **kwargs):
    update_inventory(inc_pos_dec_neg=-1, instance=instance)


@receiver(post_delete, sender=Sell)
def restored_inventory(sender, instance, **kwargs):
    update_inventory(inc_pos_dec_neg=1, instance=instance)


@receiver(post_save, sender=ShopProductInput)
def add_to_inventory(sender, instance, **kwargs):
    update_inventory(inc_pos_dec_neg=1, instance=instance)


@receiver(post_delete, sender=ShopProductInput)
def cancel_input(sender, instance, **kwargs):
    update_inventory(inc_pos_dec_neg=-1, instance=instance)
