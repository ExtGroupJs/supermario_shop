from apps.business_app.models.shop_products import ShopProducts

from apps.business_app.serializers.shop_products_logs import ShopProductsLogsSerializer

from apps.common.models.generic_log import GenericLog
from apps.common.views.generic_log import GenericLogViewSet
from django.contrib.contenttypes.models import ContentType
from django.db.models import Subquery, OuterRef, Value, F
from django.db.models.functions import Concat


class ShopProductsLogsViewSet(GenericLogViewSet):
    shop_products = ShopProducts.all_objects.filter(id=OuterRef("object_id"))

    queryset = GenericLog.objects.filter(
        content_type=ContentType.objects.get_for_model(ShopProducts),
        details__has_key="quantity",
    ).annotate(
        shop_product_name=Subquery(
            shop_products.annotate(
                full_name=Concat(
                    F("product__name"), Value(" ("), F("shop__name"), Value(")")
                )
            ).values("full_name")[:1]
        ),
        product_image=Subquery(shop_products.values("product__image")[:1]),
    )
    serializer_class = ShopProductsLogsSerializer
