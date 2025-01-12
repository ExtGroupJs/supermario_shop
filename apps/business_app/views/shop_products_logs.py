from apps.business_app.models.shop_products import ShopProducts

from apps.business_app.serializers.shop_products_logs import ShopProductsLogsSerializer

from apps.common.models.generic_log import GenericLog
from apps.common.views.generic_log import GenericLogViewSet
from django.contrib.contenttypes.models import ContentType


class ShopProductsLogsViewSet(GenericLogViewSet):
    queryset = GenericLog.objects.filter(
        details__has_key="quantity",
        content_type=ContentType.objects.get_for_model(ShopProducts),
    )
    serializer_class = ShopProductsLogsSerializer
