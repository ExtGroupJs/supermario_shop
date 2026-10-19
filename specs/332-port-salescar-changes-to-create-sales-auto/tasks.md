# Tasks 332 — Portar cambios de salescar a create_sales_auto

## Tests first

- [x] T1. Revisar el test existente
      `apps/business_app/tests/sell_group/test_sell_group_functionalities.py::TestSellGroupsViewSetFunctionalities::test_warehouse_report_lists_products_and_quantities_without_money`
      y confirmar que exige `Notas: Entrega en la tarde`.

## Implementación

- [x] T2. `templates/sales/create_sales_auto.html`: añadir bloque `#client_select`
      (select2) antes de `#client`.
- [x] T3. `static/assets/dist/js/create_sales_auto.js`: añadir `clientsUrl`,
      `clientesRegistrados`, `selectedClientId` y `cargarClientesRegistrados()`;
      invocarla en el init.
- [x] T4. Añadir handler `$("#client_select").on("change")` con readonly y reset.
- [x] T5. `crearVentas()`: enviar `client` por id u omitirlo según selección; reset
      de cliente tras crear.
- [x] T6. `crearPreVenta()`: incluir `clientName` y `paymentMethod` en el
      comprobante y resetear la selección de cliente.
- [x] T7. `buildComprobanteText()`: aceptar `sells`+shop products y `productos`.
- [x] T8. `apps/business_app/serializers/sell_group.py`
      (`_warehouse_report_lines`): añadir línea `Notas:`.

## Verificación

- [x] T9. `./venv/bin/python -m pytest -q` en verde (200 passed).
- [x] T10. `ruff check .` sin errores.
- [x] T11. Revisión manual del flujo JS: seleccionar cliente registrado, venta,
      pre-venta y reset.
