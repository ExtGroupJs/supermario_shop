# from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter

from apps.business_app.views.brand import BrandViewSet
from apps.business_app.views.model import ModelViewSet
from apps.business_app.views.product import ProductViewSet
from apps.business_app.views.shop import ShopViewSet
from apps.business_app.views.shop_products import ShopProductsViewSet
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
# (
# router.register(
# "uploaded-files",
# UploadedFilesViewSet,
# basename="uploaded-files-nodes",
# ).register(
# "allele-node-by-uploaded-file",
# AlleleNodeViewSet,
# basename="allele-node-by-uploaded-file",
# parents_query_lookups=["uploaded_file"],
# )
# )
# (
# router.register(
# "uploaded-files",
# UploadedFilesViewSet,
# basename="uploaded-files-data",
# ).register(
# "initial-file-data",
# InitialFileDataViewSet,
# basename="initial-file-data",
# parents_query_lookups=["uploaded_file"],
# )
# )
# router.register(
# "allele-nodes",
# AlleleNodeViewSet,
# basename="allele-nodes",
# )
# router.register(
# "xyz-expansion",
# InitialXyzExpansionDataViewSet,
# basename="xyz-expansion",
# )
# router.register(
# "new-coordinate-processor",
# NewCoordinatesProcessorViewSet,
# basename="new-coordinate-processor",
# )
# router.register(
# "working-copy-of-original-file-for-user",
# WorkingCopyOfOriginalFileViewSet,
# basename="working-copy-of-original-file-for-user",
# )

urlpatterns = [
    # path("layers/", list_layers, name="list_layers"),
    # path("events/", list_events, name="list_events"),
    # path("events/create/", create_event, name="create_event"),
    # path("events/get/<int:event_id>/", get_event_data_by_id, name="get_event_by_id"),
    # path("events/edit/<int:event_id>/", edit_event, name="edit_event"),
    # path("events/delete/<int:event_id>/", delete_event, name="delete_event"),
    # path("markers/", list_markers, name="list_markers"),
    # path("markers/create/", create_marker, name="create_marker"),
    # path("markers/get/", get_marker_by_description, name="get_marker_by_description"),
    # path("markers/edit/<int:marker_id>/", edit_marker, name="edit_marker"),
    # path("markers/delete/<int:marker_id>/", delete_marker, name="delete_marker"),
]

urlpatterns += router.urls
