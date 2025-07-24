from django.contrib import admin

from apps.business_app.models.brand import Brand
from apps.business_app.models.model import Model
from apps.business_app.models.product import Product
from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_product_input_group_model import (
    ShopProductInputGroup,
)
from apps.business_app.models.shop_product_input_model import ShopProductInput
from apps.business_app.models.shop_products import ShopProducts
from safedelete.admin import SafeDeleteAdmin, highlight_deleted


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = [
        "id",
        "name",
        "logo",
    ]
    fields = [
        "name",
        "logo",
    ]


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = [
        "id",
        "name",
        "brand",
        "extra_info",
    ]
    fields = [
        "name",
        "brand",
        "extra_info",
    ]


@admin.register(Product)
class ProductAdmin(SafeDeleteAdmin):
    empty_value_display = "-empty-"
    list_display = (
        highlight_deleted,
        "id",
        "name",
        "model",
        "description",
        "image",
    ) + SafeDeleteAdmin.list_display
    fields = [
        "name",
        "model",
        "description",
        "image",
    ]
    field_to_highlight = "id"


ProductAdmin.highlight_deleted_field.name = ProductAdmin.field_to_highlight


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["id", "name", "logo", "extra_info", "enabled"]
    fields = ["name", "logo", "extra_info", "enabled"]


@admin.register(ShopProducts)
class ShopProductsAdmin(SafeDeleteAdmin):
    empty_value_display = "-empty-"
    list_display = (
        highlight_deleted,
        "id",
        "shop",
        "product",
        "extra_info",
        "quantity",
        "cost_price",
        "sell_price",
        "updated_timestamp",
    ) + SafeDeleteAdmin.list_display
    fields = [
        "shop",
        "product",
        "extra_info",
        "quantity",
        "cost_price",
        "sell_price",
    ]
    field_to_highlight = "id"


@admin.register(Sell)
class SellAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = [
        "id",
        "shop_product",
        "sell_group",
        "seller",
        "extra_info",
        "quantity",
        "updated_timestamp",
    ]
    fields = [
        "shop_product",
        "seller",
        "extra_info",
        "sell_group",
        "quantity",
    ]
    search_fields = [
        "shop_product__product__name",
        "shop_product__product__model__name",
        "shop_product__product__model__brand__name",
    ]


@admin.register(SellGroup)
class SellGroupAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = [
        "id",
        "discount",
        "seller",
        "extra_info",
        "payment_method",
        "client",
    ]
    fields = [
        "discount",
        "seller",
        "extra_info",
        "payment_method",
        "client",
    ]


@admin.register(ShopProductInputGroup)
class ShopProductInputGroupAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = [
        "id",
        "for_date",
        "extra_info",
    ]
    fields = [
        "for_date",
        "extra_info",
    ]


@admin.register(ShopProductInput)
class ShopProductInputAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = [
        "id",
        "shop_product_input_group",
        "shop_product",
        "quantity",
    ]
    fields = [
        "shop_product_input_group",
        "shop_product",
        "quantity",
    ]
