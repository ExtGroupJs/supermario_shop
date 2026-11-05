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
  - `abrirModalImagenesProducto(productId)` → abre el modal compartido con el carrusel.
- Modal compartido `#modal-ver-imagenes-producto` en `templates/index.html`.
- Columna "Foto" de los listados (`/products/`, `/shop-products/`, `/inventario/`): muestra solo la imagen
  principal y, al hacer clic, abre el modal con el carrusel de todas las imágenes.
- Previsualización del producto seleccionado (shop products, create shop products y salescar): carrusel.
- Catálogo público y catálogo por mayor: carrusel en las tarjetas y en el modal de detalle.