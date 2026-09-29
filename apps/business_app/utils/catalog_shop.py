from apps.business_app.models.model import Model
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts


def in_stock_shop_products(shop_id):
    """
    Return a queryset of the `ShopProducts` rows that are actually sellable in
    the given shop, i.e. with stock left and not soft deleted.

    The soft delete of `Product` is honoured explicitly because a subquery on
    `ShopProducts` does not apply the `SOFT_DELETE_CASCADE` policy of
    `Product` on its own. Rows whose product was soft deleted must not keep a
    brand or a model in the public catalog.
    """
    return (
        ShopProducts.objects.filter(shop_id=shop_id, quantity__gt=0)
        .filter(product__deleted__isnull=True)
    )


def product_ids_in_stock(shop_id):
    """Ids of the products with stock in the given shop."""
    return in_stock_shop_products(shop_id).values("product_id")


def model_ids_in_stock(shop_id):
    """Ids of the models having at least one product with stock in the shop."""
    return in_stock_shop_products(shop_id).values("product__model_id")


def brand_ids_in_stock(shop_id):
    """
    Ids of the brands having at least one model with stock in the shop.

    `Brand` is reached through `Model` -> `Product` -> `ShopProducts`, so the
    ids are collected from the models and then resolved to their brand.
    """
    return (
        Model.objects.filter(id__in=model_ids_in_stock(shop_id))
        .values("brand_id")
        .distinct()
    )


def get_fallback_catalog_shop():
    """
    Return the shop used by the public catalog when the request does not
    specify one.

    The principal enabled shop wins; otherwise the first enabled shop is used
    as a best effort. Returns ``None`` when there is no usable shop, so callers
    can serve an empty catalog instead of failing.
    """
    return (
        Shop.objects.filter(enabled=True, principal=True).first()
        or Shop.objects.filter(enabled=True).first()
    )


def resolve_catalog_shop_id(request, param_name):
    """
    Resolve the shop id the catalog must be restricted to.

    The value of the ``param_name`` query param takes precedence. When it is
    missing or empty, it falls back to the principal enabled shop (see
    :func:`get_fallback_catalog_shop`). Returns ``None`` when no shop can be
    resolved, meaning the caller should return an empty queryset.

    Raises:
        rest_framework.exceptions.ValidationError: when the given value is not a
            positive integer, so a malformed param returns 400 instead of 500.
    """
    from rest_framework.exceptions import ValidationError

    shop_id = request.query_params.get(param_name, "").strip()
    if not shop_id:
        shop = get_fallback_catalog_shop()
        return shop.id if shop else None
    if not shop_id.isdigit():
        raise ValidationError({param_name: "Escoja una tienda válida."})
    return int(shop_id)
