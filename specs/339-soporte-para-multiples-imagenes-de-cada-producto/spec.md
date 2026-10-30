# Spec: Soporte para múltiples imágenes de cada producto

## Goal
Permitir asociar varias imágenes a un producto mediante un modelo `Gallery` (FK a `Product`), devolviendo esas imágenes en el EP de productos, sin eliminar la imagen principal existente.

## User Story
Como administrador o dueño de tienda, quiero adjuntar varias imágenes adicionales a un producto para mostrarlas en catálogo y listado de shop_products, manteniendo la imagen principal.

## Requirements (EARS)
- WHEN a product is created or updated, THE SYSTEM SHALL keep the existing main `image` field unchanged.
- WHEN gallery images are associated to a product, THE SYSTEM SHALL persist them in a `Gallery` model linked to the product.
- WHEN the products EP is consulted, THE SYSTEM SHALL return the associated gallery images for each product.
- WHEN the catalog or shop_products listing is consulted, THE SYSTEM SHALL include gallery images in the nested product data.
- WHERE a product has no gallery images, THE SYSTEM SHALL return an empty list.

## Acceptance Criteria
- `Gallery` model exists with FK to `Product` and `image` field.
- `GET /business-gestion/products/{id}/` includes `gallery` array.
- `GET/POST /business-gestion/galleries/` works for SUPER_ADMIN/SHOP_OWNER.
- Existing product image behavior remains intact.

## Out of Scope
- Full frontend detail modal in catalog/shop_products (basic input added).

## Business Rules / Permissions
- SUPER_ADMIN and SHOP_OWNER can manage products and gallery images.
- SHOP_SELLER read-only where applicable.

## Affected Entities
- Product, Gallery, ShopProducts (read nested product).