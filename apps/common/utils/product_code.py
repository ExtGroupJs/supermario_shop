def assign_product_code(product):
    brand = product.model.brand.name if product.model else ""
    model_name = product.model.name if product.model else ""

    brand_code = brand[:2].upper() or "XX"

    model_words = model_name.split()
    if model_words:
        if len(model_words) == 1:
            model_code = model_words[0][:3].upper()
        else:
            model_code = model_words[-1][:3].upper()
    else:
        model_code = "XXX"

    product_words = product.name.split()
    if len(product_words) >= 3:
        product_code = "".join(word[0] for word in product_words[:3]).upper()
    else:
        product_code = product.name[:3].upper()

    return f"{brand_code}{model_code}-{product_code}{product.pk}"