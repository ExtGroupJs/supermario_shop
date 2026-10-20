from django.contrib import admin

from apps.business_app.models.brand import Brand
from apps.business_app.models.model import Model
from apps.business_app.models.product import Product
from apps.business_app.models.sell import Sell
from apps.business_app.models.sell_group import SellGroup
from apps.business_app.models.shop import Shop
from apps.business_app.models.input_group import (
    InputGroup,
)
from apps.business_app.models.input import Input
from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.models.pallet import Pallet
from apps.common.admin import GenericModelAdmin
from safedelete.admin import SafeDeleteAdmin


class TimestampedAdmin(GenericModelAdmin):
    EXCLUDED_FIELDS_FOR_EDITING = {"created_timestamp", "updated_timestamp"}


class SafeDeleteTimestampedAdmin(SafeDeleteAdmin, TimestampedAdmin):
    EXCLUDED_FIELDS_FOR_EDITING = {
        "created_timestamp",
        "updated_timestamp",
        "deleted",
        "deleted_by_cascade",
    }


@admin.register(Brand)
class BrandAdmin(GenericModelAdmin):
    pass


@admin.register(Model)
class ModelAdmin(GenericModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(SafeDeleteTimestampedAdmin):
    pass


@admin.register(Shop)
class ShopAdmin(GenericModelAdmin):
    pass


@admin.register(ShopProducts)
class ShopProductsAdmin(SafeDeleteTimestampedAdmin):
    EXCLUDED_FIELDS_FOR_EDITING = {
        "created_timestamp",
        "updated_timestamp",
        "deleted",
        "deleted_by_cascade",
        "cost_price",
    }


@admin.register(Pallet)
class PalletAdmin(GenericModelAdmin):
    pass


@admin.register(Sell)
class SellAdmin(TimestampedAdmin):
    search_fields = [
        "shop_product__product__name",
        "shop_product__product__model__name",
        "shop_product__product__model__brand__name",
    ]


@admin.register(SellGroup)
class SellGroupAdmin(TimestampedAdmin):
    pass


@admin.register(InputGroup)
class InputGroupAdmin(TimestampedAdmin):
    pass


@admin.register(Input)
class InputAdmin(TimestampedAdmin):
    pass
