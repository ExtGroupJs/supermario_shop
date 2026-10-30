# Design

## Templates followed
- Model: `apps/business_app/models/product.py` (SafeDeleteModel + BaseModel pattern).
- Serializer: `apps/business_app/serializers/product.py` (write/read split).
- ViewSet: `apps/business_app/views/product.py`.

## Changes
- New model `Gallery` in `apps/business_app/models/gallery.py` (plain `models.Model`, FK `CASCADE`), re-exported.
- New serializer `apps/business_app/serializers/gallery.py`.
- New viewset `apps/business_app/views/gallery.py`.
- URLs registered as `galleries` and alias `gallery`.
- `ReadProductSerializer` and `CatalogProductSerializer` embed `gallery`.
- `ProductViewSet` sets `retrieve_serializer_class` and prefetches gallery.
- Migration `0036_gallery`.
- Frontend inputs and upload in `createproducts.js` and `products.js`.