from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import GenericAPIView

from apps.business_app.models.shop_products import ShopProducts
from apps.business_app.serializers.shop_products import (
    CatalogShopProductSerializer,
    ReadShopProductsSerializer,
    ShopProductsSerializer,
)

from apps.business_app.serializers.shop_products_logs import ShopProductsLogsSerializer
from apps.common.common_ordering_filter import CommonOrderingFilter
from apps.common.mixins.serializer_map import SerializerMapMixin

from apps.common.models.generic_log import GenericLog
from apps.common.pagination import AllResultsSetPagination
from apps.common.permissions import ShopProductsViewSetPermission
from rest_framework.permissions import AllowAny
from rest_framework.permissions import AllowAny
from apps.common.views.generic_log import GenericLogViewSet
from apps.users_app.models.groups import Groups
from apps.users_app.models.system_user import SystemUser
from rest_framework.decorators import action
from django.db.models import Count, Sum, F, Value
from rest_framework.response import Response
from django.db.models.functions import Concat
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers


class ShopProductsLogsViewSet(GenericLogViewSet):
    queryset = GenericLog.objects.filter(details__has_key="quantity")
    serializer_class = ShopProductsLogsSerializer
