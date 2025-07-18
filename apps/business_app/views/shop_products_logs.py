from apps.business_app.filters.shop_products_logs import ShopProductsLogsFilter
from apps.business_app.models.shop_products import ShopProducts

from apps.business_app.serializers.shop_products_logs import ShopProductsLogsSerializer

from apps.common.models.generic_log import GenericLog
from apps.common.views.generic_log import GenericLogViewSet
from django.contrib.contenttypes.models import ContentType
from django.db.models import Subquery, OuterRef, Value, F
from django.db.models.functions import Concat


class ShopProductsLogsViewSet(GenericLogViewSet):
    # Prefetch the content type once
    shop_product_content_type = ContentType.objects.get_for_model(ShopProducts)

    # Get all needed shop product data in a single subquery
    shop_products_subquery = (
        ShopProducts.objects.filter(id=OuterRef("object_id"))
        .annotate(
            full_name=Concat(
                F("product__name"),
                Value(" ("),
                F("product__model__brand__name"),
                Value(" - "),
                F("product__model__name"),
                Value(")"),
                Value(" ("),
                F("shop__name"),
                Value(")"),
            )
        )
        .values("full_name", "product__image", "shop")
    )

    queryset = GenericLog.objects.filter(
        content_type=shop_product_content_type,
        details__has_key="quantity",
    ).annotate(
        shop_product_name=Subquery(shop_products_subquery.values("full_name")[:1]),
        product_image=Subquery(shop_products_subquery.values("product__image")[:1]),
        shop=Subquery(shop_products_subquery.values("shop")[:1]),
    )
    serializer_class = ShopProductsLogsSerializer
    search_fields = [
        "shop_product_name",
    ]
    ordering_fields = [
        "shop_product_name",
        "created_timestamp",
    ]
    ordering = [
        "shop_product_name",
    ]
    filterset_class = ShopProductsLogsFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            shop_product_name__isnull=False
        )  # this grants the logs are returned for non deleted shop_products
