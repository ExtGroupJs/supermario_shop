"""
Shared annotations of the sell listings.

The columns a sell table renders (product name, unit price, extended amount, profit)
do not exist on the ``Sell`` model; they are computed by the database. Both the sells
listing and the group sells listing need the very same expressions, so they are built
here once instead of being copy pasted per viewset: if the product label ever changes,
there is a single place to change it.
"""

from django.db.models import F, Value
from django.db.models.functions import Coalesce, Concat


def product_name(with_shop=False):
    """
    Annotation that labels a sell product as ``Nombre (Marca - Modelo)``.

    ``with_shop`` appends the shop name. The owner sees every shop in the same
    listing, so it needs the shop to tell two identical products apart; a seller
    only ever sees its own shop, so the shop is left out for it.
    """
    label = Concat(
        F("shop_product__product__name"),
        Value(" ("),
        F("shop_product__product__model__brand__name"),
        Value(" - "),
        F("shop_product__product__model__name"),
        Value(") "),
    )
    if not with_shop:
        return label
    return Concat(label, Value(" - "), F("shop_product__shop__name"))


def profits():
    """Annotation of what a sell earns, once the cost price is taken off."""
    return (
        F("shop_product__sell_price") - Coalesce(F("shop_product__cost_price"), 0.0)
    ) * F("quantity")


def line_totals():
    """Annotations of the unit price and the extended amount of a sell."""
    return {
        "total_priced": F("quantity") * F("shop_product__sell_price"),
        "sell_price": F("shop_product__sell_price"),
    }
