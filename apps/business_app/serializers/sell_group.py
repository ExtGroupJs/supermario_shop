from decimal import Decimal

from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import serializers


from apps.business_app.models.sell_group import SellGroup
from apps.business_app.serializers.sell import SellSerializer
from apps.clients_app.models.client import Client

two_decimals = Decimal("0.01")


class SellGroupSerializer(serializers.ModelSerializer):
    updated_timestamp = serializers.SerializerMethodField()
    sells = SellSerializer(many=True)
    client_name = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    client_phone = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = SellGroup
        fields = (
            "id",
            "discount",
            "extra_info",
            "payment_method",
            "seller",
            "updated_timestamp",
            "for_date",
            "sells",
            "client",
            "total",
            "client_name",
            "client_phone",
        )
        read_only_fields = ("id",)

    def get_updated_timestamp(self, object):
        return object.updated_timestamp.strftime("%d-%h-%Y a las  %I:%M %p")

    def _report_lines(self, sell_group):
        """
        Describe a sell group the same way the receipt printed right after a sale.

        Kept as plain text lines so the report can be copied to the clipboard as it
        is, and the rows can be assembled server side, where the sell data needed to
        build it is actually available.
        """
        payment_method = (
            "Zelle"
            if sell_group.payment_method == SellGroup.PAYMENT_METODS.ZELLE
            else "USD"
        )
        client_name = sell_group.client.name if sell_group.client else ""
        date_str = sell_group.for_date.astimezone(
            timezone.get_current_timezone()
        ).strftime("%d-%b-%Y %I:%M %p")

        lines = [
            "COMPROBANTE DE VENTA",
            f"Nro: {sell_group.id}",
            f"Fecha: {date_str}",
            f"Cliente: {client_name}",
            f"Metodo de pago: {payment_method}",
            "------------------------------",
            "PRODUCTOS:",
        ]

        for index, sell in enumerate(sell_group.sells.all(), start=1):
            # The sells are read straight from the model, so the price and the
            # product name have to be resolved here instead of being read off the
            # annotations the sells listing adds in its queryset.
            unit_price = Decimal(str(sell.shop_product.sell_price or 0))
            quantity = sell.quantity
            subtotal = unit_price * quantity
            product_name = sell.shop_product.product.__str__()
            lines += [
                f"{index}. {product_name}",
                f"   Cantidad: {quantity}",
                f"   Precio: ${unit_price.quantize(two_decimals)}",
                f"   Subtotal: ${subtotal.quantize(two_decimals)}",
            ]

        discount = Decimal(sell_group.discount)
        total = Decimal(sell_group.total or 0)
        net_total = max(total - discount, Decimal("0.00"))

        lines += [
            "------------------------------",
            f"Subtotal: ${total.quantize(two_decimals)}",
            f"Descuento: ${discount.quantize(two_decimals)}",
            f"Total: ${net_total.quantize(two_decimals)}",
            f"Notas: {sell_group.extra_info or ''}",
        ]
        return lines

    def get_report(self, sell_group):
        """Plain text receipt of a sell group, ready to be copied to the clipboard."""
        return "\n".join(self._report_lines(sell_group))

    def validate_sells(self, value: list):
        if len(value) < 1:
            raise ValidationError("La venta debe contener al menos un elemento")
        # ``shop_product`` is already a ShopProducts instance here, so the shop of the
        # first item is the shop the whole sell group belongs to. It is resolved at
        # validation time because the view pops "sells" out of validated_data before
        # saving, and it is reused by create() to place the client on that same shop.
        self._shop = getattr(value[0].get("shop_product"), "shop", None)
        return value

    def create(self, validated_data: dict):
        """Resolve the sell group client from the name/phone pair sent by the sales views.

        The client is looked up by phone (its natural unique key), so the same phone
        always maps to the same client. When the phone is unknown a new client is
        created; when it is already registered only its name is refreshed. Without a
        phone there is no reliable key to match a client, so the name is ignored and
        the sell group is stored without client.
        """
        client_name = validated_data.pop("client_name", "").strip()
        client_phone = validated_data.pop("client_phone", "").strip()
        shop = getattr(self, "_shop", None)

        if shop is None:
            # A client always belongs to a shop, so without one there is nothing
            # to resolve and the sell group is stored without client.
            return super().create(validated_data)

        if client_phone:
            client = Client.objects.filter(phone=client_phone).first()
            if client is None:
                client = Client.objects.create(
                    name=client_name,
                    phone=client_phone,
                    shop=shop,
                )
            elif client_name and client.name != client_name:
                client.name = client_name
                client.save(update_fields=["name"])
            validated_data["client"] = client
        return super().create(validated_data)

    def validate_for_date(self, value):
        if value > timezone.now():
            raise ValidationError(
                "La fecha de la venta no puede ser mayor al momento actual"
            )
        return value
