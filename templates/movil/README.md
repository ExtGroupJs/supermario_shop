# Convencion de Vistas Moviles

Esta carpeta agrupa las vistas optimizadas para telefono.

## Estructura base

- Templates moviles:
  - `templates/movil/<modulo>/<nombre_vista>_movil.html`
- JavaScript movil:
  - `static/assets/dist/js/movil/<modulo>/<nombre_vista>_movil.js`

Ejemplo actual:

- `templates/movil/shop_products/move_shop_products_auto_movil.html`
- `static/assets/dist/js/movil/shop_products/move_shop_products_auto_movil.js`

## Convencion de nombres

- Sufijo de template y JS: `_movil`
- Nombre de vista Django: `<nombre_base>_movil`
- URL: `<nombre_base>_movil/`
- Name de URL: `<nombre_base>_movil`

Ejemplo:

- Vista: `shop_products_move_auto_movil`
- URL: `shop_products_move_auto_movil/`
- Name: `shop_products_move_auto_movil`

## Flujo para agregar una nueva vista movil

1. Crear template en `templates/movil/<modulo>/`.
2. Crear JS en `static/assets/dist/js/movil/<modulo>/`.
3. Registrar la funcion en `apps/users_app/views/pages.py`.
4. Registrar la URL en `project_site/urls.py`.
5. Referenciar en el template el JS movil con `{% static %}`.

## Reglas sugeridas de UX movil

- Controles tactiles con altura minima de 44px.
- Botones principales en ancho completo (`btn-block`) cuando aplique.
- Evitar tablas anchas; preferir tarjetas/listas.
- Mantener acciones importantes visibles (por ejemplo, barra inferior sticky).

## Nota de navegacion

Las vistas moviles pueden publicarse sin acceso en menu cuando se requiera acceso directo por URL.
