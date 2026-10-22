# Spec 335 — Emitir salida del almacén en la misma vista de las ventas

- Issue: #335 — Emitir salida del almacén en la misma vista de las ventas
- Rama: `335-emitir-salida-del-almacen-en-la-misma-vista-de-las-ventas`
- Estado: Implementado (retroactivo al flujo SDD)

## Objetivo
Añadir en la vista `salescar` un botón con la misma funcionalidad que "Comprobante para Almacén" que existe en la tabla de la vista `group_sells`, entre los botones "Crear Preventa" y "Crear Venta". Usar como `group_sell` id el último recibido en la respuesta `201` al completar la venta desde `salescar`.

## Alcance
- Plantilla `templates/sales_products/salescar.html`: añadir botón `Comprobante para Almacén` entre `#crearPreVenta` y `#crearVenta`
- JS `static/assets/dist/js/salescar.js`: guardar `lastSellGroupId` al crear venta, añadir handler que llame a `GET /business-gestion/sell-groups/{id}/warehouse-report/` y muestre modal con opción a copiar (mismo patrón que `group_sells.js`)

## Fuera de alcance
- Cambios en backend
- Cambios en `group_sells`
- Cambios en otros flujos de venta

## Criterios de aceptación
1. En `salescar` aparece el botón "Comprobante para Almacén" entre "Crear Pre-venta" y "Crear Venta".
2. Tras crear una venta con éxito (respuesta 201), se guarda el `id` del `SellGroup` devuelto.
3. Al pulsar "Comprobante para Almacén", se consulta `GET /business-gestion/sell-groups/{id}/warehouse-report/` con ese id y se muestra el comprobante (sin datos de cliente/método de pago/montos), con opción a copiar al portapapeles.
4. Si no hay venta reciente, se muestra aviso al usuario.
