from datetime import timedelta
import datetime
from rest_framework import serializers

from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.product import (
    CatalogProductSerializer,
    ReadProductSerializer,
)
from apps.users_app.models.groups import Groups


class ShopProductsSerializer(serializers.ModelSerializer):
    updated_timestamp = serializers.SerializerMethodField()

    shop_name = serializers.CharField(read_only=True)
    product_name = serializers.CharField(read_only=True)

    class Meta:
        model = ShopProducts
        fields = (
            "id",
            "quantity",
            "cost_price",
            "sell_price",
            "shop",
            "shop_name",
            "product",
            "product_name",
            "extra_info",
            "created_timestamp",
            "updated_timestamp",
            "__repr__",
        )

    def get_updated_timestamp(self, object):
        return object.updated_timestamp.strftime("%d-%h-%Y")
        # return object.updated_timestamp.strftime("%d-%h-%Y a las  %I:%M %p") # con hora


class ReadShopProductsSerializer(ShopProductsSerializer):
    product = ReadProductSerializer(read_only=True)
    product_name = serializers.CharField(read_only=True)
    sales_count = serializers.IntegerField(default=0)

    class Meta(ShopProductsSerializer.Meta):
        model = ShopProducts
        fields = ShopProductsSerializer.Meta.fields + ("sales_count",)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        request = self.context.get("request")
        if (
            request
            and request.user.groups.exclude(
                id__in=[Groups.SHOP_OWNER.value, Groups.SUPER_ADMIN.value]
            ).exists()
        ):
            response.pop("cost_price", None)
        return response


class CatalogShopProductSerializer(ReadShopProductsSerializer):
    one_month_ago = datetime.datetime.now() - timedelta(days=30)
    product = CatalogProductSerializer(read_only=True)

    class Meta(ReadShopProductsSerializer.Meta):
        fields = (
            "id",
            "sell_price",
            "product",
            "shop_name",
            "sales_count",
            "extra_info",
            "__repr__",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["is_new"] = instance.updated_timestamp >= self.one_month_ago
        return response


class MoveToAnotherShopSerializer(serializers.ModelSerializer):
    default_error_messages = dict(
        serializers.ModelSerializer.default_error_messages,
        destiny_shop_must_be_diferent="No puedes mover el producto a la misma tienda.",
        quantity_lesser_than_one="La cantidad debe ser mayor que cero.",
        quantity_greater_than_available="La cantidad a mover no puede ser mayor que la cantidad disponible.",
    )

    class Meta:
        model = ShopProducts
        fields = (
            "shop",
            "quantity",
        )

    def validate_shop(self, new_shop):
        if new_shop == self.instance.shop:
            self.fail("destiny_shop_must_be_diferent")
        return new_shop

    def validate_quantity(self, quantity):
        if quantity < 1:
            self.fail("quantity_lesser_than_one")
        if quantity > self.instance.quantity:
            self.fail("quantity_greater_than_available")
        return quantity

    def save(self, **kwargs):
        new_shop = self.validated_data["shop"]
        quantity_to_move = self.validated_data["quantity"]
        product = self.instance.product

        # Buscar si ya existe un ShopProducts en el shop destino con el mismo producto
        extra_log_info = f"(transferido desde {self.instance.shop})"
        try:
            dest_shop_product = ShopProducts.objects.get(shop=new_shop, product=product)
            dest_shop_product.quantity += quantity_to_move
            dest_shop_product.save(
                update_fields=["quantity"], extra_log_info=extra_log_info
            )
        except ShopProducts.DoesNotExist:
            # Crear nuevo registro en el shop destino
            ShopProducts.objects.create(
                shop=new_shop,
                product=product,
                quantity=quantity_to_move,
                cost_price=self.instance.cost_price,
                sell_price=self.instance.sell_price,
                extra_info=self.instance.extra_info,
                extra_log_info=extra_log_info,
            )
        self.instance.quantity -= quantity_to_move
        self.instance.save(
            update_fields=["quantity"], extra_log_info=f"(transferido a {new_shop})"
        )
        return self.instance
