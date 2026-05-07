# from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter

from apps.business_app.views.brand import BrandViewSet
from apps.business_app.views.dashboard import DashboardViewSet
from apps.business_app.views.model import ModelViewSet
from apps.business_app.views.product import ProductViewSet
from apps.business_app.views.sell_group import PaymentMethodsViewSet, SellGroupViewSet
from apps.business_app.views.shop import ShopViewSet
from apps.business_app.views.input_group import (
    InputGroupViewSet,
)
from apps.business_app.views.input import InputViewSet
from apps.business_app.views.shop_products import ShopProductsViewSet
from apps.business_app.views.sell import SellViewSet
from apps.business_app.views.shop_products_logs import ShopProductsLogsViewSet


router = ExtendedSimpleRouter()


router.register(
    "brands",
    BrandViewSet,
    basename="brands",
)
router.register(
    "models",
    ModelViewSet,
    basename="models",
)
router.register(
    "products",
    ProductViewSet,
    basename="products",
)
router.register(
    "shops",
    ShopViewSet,
    basename="shop",
)
router.register(
    "shop-products",
    ShopProductsViewSet,
    basename="shop-products",
)
router.register(
    "shop-products-logs",
    ShopProductsLogsViewSet,
    basename="shop-products-logs",
)
router.register(
    "sell-products",
    SellViewSet,
    basename="sell-products",
)
router.register(
    "sell-groups",
    SellGroupViewSet,
    basename="sell-groups",
)
router.register(
    "dashboard",
    DashboardViewSet,
    basename="dashboard",
)
router.register(
    "payment-methods",
    PaymentMethodsViewSet,
    basename="payment-methods",
)
router.register(
    "input-groups",
    InputGroupViewSet,
    basename="input-groups",
)
router.register(
    "input-products",
    InputViewSet,
    basename="input-products",
)

urlpatterns = []

urlpatterns += router.urls
