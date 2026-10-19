# Design 332 — Portar cambios de salescar a create_sales_auto

## Approach

Es un porte de UI/JS con un ajuste mínimo en backend. No se crean capas nuevas.
Se copia el patrón ya vigente en `salescar` (`#client_select` + lógica de cliente
registrado) dentro de `create_sales_auto`, que hoy no lo tiene.

## Existing files used as template

- Cliente registrado (fuente): `static/assets/dist/js/salescar.js`
  - `clientsUrl`, `clientesRegistrados`, `selectedClientId`
  - handler `$("#client_select").on("change", ...)`
  - payload `if (selectedClientId) { payload.client = ...; delete client_name/phone }`
  - reset post-venta del selector.
- Plantilla de referencia: `templates/sales_products/salescar.html` (bloque
  `#client_select` con select2, líneas ~103-110).

## Template changes — `templates/sales/create_sales_auto.html`

- Añadir, antes del campo `#client`, un bloque `form-group` con
  `select#client_select.select2` con la opción `— Nuevo cliente —`.
- No se añaden CSS/JS nuevos: select2 ya está cargado en la página.

## JS changes — `static/assets/dist/js/create_sales_auto.js`

- Constantes/estado nuevos: `clientsUrl`, `clientesRegistrados`, `selectedClientId`.
- Al iniciar (`$(function(){...})`): llamar `cargarClientesRegistrados()`.
- `cargarClientesRegistrados()`: `GET clientsUrl`, poblar `#client_select`, aplicar
  select2. Errores solo a consola (no bloquea la venta).
- Handler `$("#client_select").on("change")`:
  - con valor: guardar `selectedClientId`, rellenar `#client`/`#client_phone` y
    ponerlos `readonly`.
  - sin valor: limpiar, quitar `readonly`, `selectedClientId = null`.
- `crearVentas()`: tras construir `payload`, si `selectedClientId` existe,
  `payload.client = selectedClientId` y borrar `client_name`/`client_phone`.
  El nombre sigue siendo obligatorio para el flujo de cliente nuevo.
- Reset: tanto en el `then` de `crearVentas()` como al final de `crearPreVenta()`,
  limpiar `#client`, `#client_phone`, `#client_select` y `selectedClientId`.
- `buildComprobanteText()` acepta ambos formatos (`sells`+shop products y
  `productos`), para poder reutilizarlo igual que en salescar.
- `crearPreVenta()`: incluir `clientName` y `paymentMethod` en el comprobante.

## Backend change — `apps/business_app/serializers/sell_group.py`

- `_warehouse_report_lines()`: añadir `f"Notas: {sell_group.extra_info or ''}"`
  tras la línea separadora final, para que el comprobante de almacén incluya las
  notas (criterio del test existente).

## Tests

- Backend: `apps/business_app/tests/sell_group/test_sell_group_functionalities.py`
  - `test_warehouse_report_lists_products_and_quantities_without_money` ya
    espera `Notas: Entrega en la tarde` → el cambio lo satisface.
- JS: no hay suite JS en el repo; verificación manual del flujo y `pytest` completo.

## Minimal touchpoints

| Archivo | Cambio |
|---|---|
| `templates/sales/create_sales_auto.html` | bloque `#client_select` |
| `static/assets/dist/js/create_sales_auto.js` | cliente registrado + payload + reset + comprobante |
| `apps/business_app/serializers/sell_group.py` | línea `Notas:` en comprobante de almacén |
| `apps/users_app/views/pages.py` | sin cambio funcional (se descarta el decorador añadido en el intento previo) |
