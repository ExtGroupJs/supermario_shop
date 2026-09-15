def assign_product_code(product):
    """Generate a short product code using brand, model, and product-name initials.

    The code is composed of the first two letters of the brand, the model code,
    the initials of up to the first three words in the product name, and the
    product primary key. Missing brand or model information falls back to default
    placeholder values so the code remains valid and consistent.
    """
    brand = product.model.brand.name if product.model else ""
    model_name = product.model.name if product.model else ""

    brand_code = brand[:2].upper() or "XX"

    model_words = model_name.split()
    if model_words:
        if len(model_words) == 1:
            model_code = model_words[0][:3].upper()
        else:
            model_code = "".join(word[0] for word in model_words[:3]).upper()
    else:
        model_code = "XXX"

    product_words = product.name.split()
    if len(product_words) >= 3:
        product_code = "".join(word[0] for word in product_words[:3]).upper()
    else:
        product_code = product.name[:3].upper()

    return f"{brand_code}{model_code}-{product_code}{product.pk}".upper()