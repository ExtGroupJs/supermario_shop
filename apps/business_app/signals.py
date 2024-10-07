from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.business_app.models.sell import Sell
from apps.business_app.models.shop_products import ShopProducts


def update_inventory(increment):
    """
    The increment only defines the operation, if is -1 the value is decremented, if +1, incremented
    """

    def decorator(func):
        def wrapper(sender, instance, **kwargs):
            related_product = ShopProducts.objects.get(id=instance.shop_product.id)
            related_product.quantity += increment * instance.quantity
            related_product.save(update_fields=["quantity"])
            return func(sender, instance, **kwargs)

        return wrapper

    return decorator


@receiver(post_save, sender=Sell)
def remove_from_inventory(sender, instance, **kwargs):
    related_product = ShopProducts.objects.get(id=instance.shop_product.id)
    related_product.quantity += instance.quantity
    related_product.save(update_fields=["quantity"])


@receiver(post_delete, sender=Sell)
def restored_inventory(sender, instance, **kwargs):
    
    related_product = ShopProducts.objects.get(id=instance.shop_product.id)
    related_product.quantity -= instance.quantity
    related_product.save(update_fields=["quantity"])
