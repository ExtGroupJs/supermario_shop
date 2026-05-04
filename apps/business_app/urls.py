# from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter

from apps.business_app.views.brand import BrandViewSet
from apps.business_app.views.dashboard import DashboardViewSet
from apps.business_app.views.model import ModelViewSet
from apps.business_app.views.product import ProductViewSet
from apps.business_app.views.sell_group import PaymentMethodsViewSet, SellGroupViewSet
from apps.business_app.views.shop import ShopViewSet
from apps.business_app.views.shop_product_input_group_viewset import (
    ShopProductInputGroupViewSet,
)
from apps.business_app.views.shop_products import ShopProductsViewSet
from apps.business_app.views.sell import SellViewSet
from apps.business_app.views.shop_products_logs import ShopProductsLogsViewSet


# from django.urls import path

# from apps.business_app.views import (
# AllowedExtensionsViewSet,
# SiteConfigurationViewSet,
# UploadedFilesViewSet,
# InitialFileDataViewSet,
# NewCoordinatesProcessorViewSet,
# )
# from apps.business_app.views.allele_nodes import AlleleNodeViewSet
# from apps.business_app.views.event_markers import (
# edit_event,
# list_events,
# get_event_data_by_id,
# create_event,
# delete_event,
# list_markers,
# get_marker_by_description,
# create_marker,
# edit_marker,
# delete_marker,
# )
# from apps.business_app.views.layers import list_layers

# from apps.business_app.views.initial_xyz_expansion_data import (
# InitialXyzExpansionDataViewSet,
# )
# from apps.business_app.views.working_copy_of_original_file import (
# WorkingCopyOfOriginalFileViewSet,
# )

router = ExtendedSimpleRouter()
# router.register(
# "allowed-extensions",
# AllowedExtensionsViewSet,
# basename="allowed-extensions",
# )
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
    "shop-product-input-group",
    ShopProductInputGroupViewSet,
    basename="shop-product-input-group",
)

urlpatterns = []

urlpatterns += router.urls
