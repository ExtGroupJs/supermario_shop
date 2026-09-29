from apps.business_app.models.shop import Shop


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
