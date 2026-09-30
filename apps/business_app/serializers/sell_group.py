from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import serializers


from apps.business_app.models.sell_group import SellGroup
from apps.business_app.serializers.sell import SellSerializer
from apps.clients_app.models.client import Client


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
