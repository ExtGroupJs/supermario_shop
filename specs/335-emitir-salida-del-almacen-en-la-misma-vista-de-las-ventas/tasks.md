# Tasks 335 — Emitir salida del almacén en la misma vista de las ventas

## Pre-requisitos
- [x] Issue #335 creado/asignado
- [x] Rama `335-emitir-salida-del-almacen-en-la-misma-vista-de-las-ventas` activa
- [x] Verificado endpoint `GET /business-gestion/sell-groups/{id}/warehouse-report/` existente y usado en `group_sells`

## Implementación
- [x] Añadir botón `#comprobanteAlmacen` en `templates/sales_products/salescar.html` entre `#crearPreVenta` y `#crearVenta`
- [x] Añadir `lastSellGroupId` en `static/assets/dist/js/salescar.js`
- [x] Guardar `lastSellGroupId = response.data?.id` tras éxito de venta (201)
- [x] Añadir handler para `#comprobanteAlmacen` con llamada al endpoint warehouse-report, modal y copia al portapapeles
- [x] Validación: aviso si no hay venta reciente

## Verificación
- [x] Cambios solo en archivos frontend (plantilla + JS). Sin tocar backend.
- [x] Sigue patrón existente (endpoint + UX) usado en `group_sells.js`
- [ ] Revisión manual en `salescar`: crear venta → aparece botón funcional → genera comprobante de almacén

## Aprobación
- [ ] **Aprobación explícita requerida** del `tasks.md` antes de dar por concluido según flujo SDD
