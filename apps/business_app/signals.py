from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.business_app.models.sell import Sell
from apps.business_app.models.shop_product_input_model import ShopProductInput
from apps.business_app.models.shop_products import ShopProducts
from twilio.rest import Client



def update_inventory(inc_pos_dec_neg, instance):
    """
    The increment only defines the operation, if is -1 the value is decremented, if +1, incremented
    """
    shop_product = ShopProducts.objects.filter(id=instance.shop_product.id).first()
    if shop_product:
        shop_product.quantity += inc_pos_dec_neg * instance.quantity
        extra_log_info = None
        extra = ""
        if isinstance(instance, ShopProductInput) and instance.shop_product_input_group:
            if inc_pos_dec_neg == -1:
                extra = " cancelada"
            extra_log_info = f"Entrada del {instance.shop_product_input_group.for_date.strftime('%d-%h-%Y')}{extra}"
        elif isinstance(instance, Sell) and instance.sell_group:
            if inc_pos_dec_neg == 1:
                extra = " cancelada"
            extra_log_info = (
                f"Venta del {instance.sell_group.for_date.strftime('%d-%h-%Y')}{extra}"
            )
        shop_product.save(update_fields=["quantity"], extra_log_info=extra_log_info)


@receiver(post_save, sender=Sell)
def remove_from_inventory(sender, instance, **kwargs):
    update_inventory(inc_pos_dec_neg=-1, instance=instance)
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body='¡Hola desde Twilio!. Mario, dime si esta mierda te llegó. Atentamente: El ratón secuestrador',
        from_=settings.TWILIO_DEFAULT_CALLERID,
        to="+1 (305) 877-0178",
    )
    print("------------------message.sid")
    print(message.sid)


@receiver(post_delete, sender=Sell)
def restored_inventory(sender, instance, **kwargs):
    update_inventory(inc_pos_dec_neg=1, instance=instance)


@receiver(post_save, sender=ShopProductInput)
def add_to_inventory(sender, instance, **kwargs):
    update_inventory(inc_pos_dec_neg=1, instance=instance)


@receiver(post_delete, sender=ShopProductInput)
def cancel_input(sender, instance, **kwargs):
    update_inventory(inc_pos_dec_neg=-1, instance=instance)
