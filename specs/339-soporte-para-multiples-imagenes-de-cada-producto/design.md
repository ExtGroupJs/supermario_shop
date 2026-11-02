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
- Shared carousel helper `static/assets/dist/js/product-gallery.js`:
  - `imagenesProducto(producto)` → imagen principal + galería.
  - `carruselProductoHtml(producto, opciones)` → HTML de un carrusel Bootstrap 4.
  - `inicializarCarruselesProducto(contenedor)` → inicializa los carruseles renderizados.
- El carrusel se usa en: lista de productos (`products.js`), lista de shop products
  (`shop_products.js`), inventario (`inventario.js`), previsualización del producto
  seleccionado (shop products, create shop products y salescar), catálogo público y
  catálogo por mayor (tarjetas y modal de detalle).