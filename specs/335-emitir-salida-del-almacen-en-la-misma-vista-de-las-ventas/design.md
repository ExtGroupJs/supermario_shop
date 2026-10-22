# Design 335 — Emitir salida del almacén en la misma vista de las ventas

## Referencia existente
- Endpoint ya existente: `apps/business_app/views/sell_group.py` (`warehouse_report` action) — `GET /business-gestion/sell-groups/{pk}/warehouse-report/`
- Serializador: `apps/business_app/serializers/sell_group.py` `SellGroupSerializer.get_warehouse_report()` / `_warehouse_report_lines()` (sin cliente/pago/montos)
- Uso en vista listado: `static/assets/dist/js/group_sells.js` `generarComprobanteAlmacen()` llama al mismo endpoint con spinner, modal con `buildInformeHtml` + `copiarComprobante`

## Cambios

### 1) `templates/sales_products/salescar.html`
Añadir botón entre "Crear Pre-venta" y "Crear Venta":
```html
<button type="button" class="btn btn-info ml-2" id="comprobanteAlmacen">Comprobante para Almacén</button>
```

### 2) `static/assets/dist/js/salescar.js`
- Añadir variable global `let lastSellGroupId = null;`
- Tras `201` en `#crearVenta` handler, guardar `lastSellGroupId = response.data?.id;` (antes de mostrar comprobante/limpiar formulario)
- Añadir handler `#comprobanteAlmacen` click:
  - Si no hay `lastSellGroupId` → Swal warning
  - Llamar `GET /business-gestion/sell-groups/${lastSellGroupId}/warehouse-report/` con `X-CSRFToken` (axios)
  - Mostrar modal con reporte, botones "Copiar comprobante"/"Cerrar", copiar con fallback
  - Deshabilitar botón con spinner durante petición

Patrón reutilizado: mismo endpoint, mismo formato de respuesta `{report: "..."}`, misma UX de copia que `group_sells.js`.

## Notas
- No se modifica backend. El endpoint ya cumple los requisitos.
- Se usa el `id` devuelto por la respuesta exitosa de creación de venta (`sell-groups/` POST) como indica el issue.
