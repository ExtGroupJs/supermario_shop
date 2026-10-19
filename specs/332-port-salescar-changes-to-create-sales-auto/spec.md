# Spec 332 — Portar cambios de salescar a create_sales_auto

- Issue: #332 — Portar cambios de salescar a create_sales_auto
- Label: `BE-feature`
- Rama: `feature/332-port-salescar-changes-to-create-sales-auto`

## Goal

Que la vista de venta automática `create_sales_auto` comparta con la vista `salescar`
el comportamiento más reciente: elegir un cliente ya registrado, enviar la venta
asociada a ese cliente o a uno nuevo, y generar el comprobante (venta y pre-venta)
con la misma información.

## User Story

Como vendedor, quiero usar la vista de venta automática igual que la venta por
producto (`salescar`): poder seleccionar un cliente registrado para no reescribir
sus datos, y obtener un comprobante completo, tanto al crear la venta como al
generar una pre-venta.

## Requirements

1. `create_sales_auto.html` incluye un selector de cliente registrado
   (`#client_select`, select2) además de los campos de nombre y teléfono.
2. Al elegir un cliente registrado, nombre y teléfono se rellenan y quedan en solo
   lectura. Al volver a "— Nuevo cliente —", vuelven a ser editables y se vacían.
3. La carga inicial del selector usa `GET /client-gestion/clients/`.
4. Al crear la venta (`crearVentas`), si hay cliente registrado seleccionado se
   envía `client` (id) y se omiten `client_name`/`client_phone`; si no, se envían
   `client_name`/`client_phone` como hasta ahora.
5. La pre-venta (`crearPreVenta`) refleja el cliente y el método de pago en el
   comprobante local y luego resetea la selección de cliente.
6. Tras crear la venta o la pre-venta, `#client_select`, `#client` y
   `#client_phone` quedan reseteados.
7. El comprobante de almacén (`get_warehouse_report` en
   `SellGroupSerializer`) incluye la línea `Notas:` para mantener paridad con el
   comprobante de venta.

## Acceptance Criteria

- [ ] La vista `create_sales_auto` muestra el selector de cliente registrado.
- [ ] Elegir un cliente rellena nombre/teléfono en solo lectura; elegir "Nuevo
      cliente" los libera y vacía.
- [ ] La venta enviada lleva `client` (id) cuando se eligió cliente registrado.
- [ ] La venta enviada lleva `client_name`/`client_phone` cuando es un cliente nuevo.
- [ ] La pre-venta muestra cliente y método de pago en el comprobante.
- [ ] Tras crear venta o pre-venta, el selector y los campos quedan vacíos.
- [ ] `pytest` en verde y `ruff check .` sin errores.
- [ ] El comprobante de almacén incluye `Notas: <extra_info>`.

## Out of Scope

- Cambios en el motor de parseo del mensaje de venta.
- Nuevos endpoints de backend o cambios de modelo/migraciones.
- Cambios en `salescar`, `create_sales_auto_movil` u otras vistas.

## Business Rules / Permissions

- `create_sales_auto` mantiene su comportamiento de acceso actual (sin
  `@user_passes_test(is_owner)`), igual que `salescar`.
- Un cliente registrado se identifica por `id`; uno nuevo por `name`/`phone`.

## Affected Entities

- `templates/sales/create_sales_auto.html`
- `static/assets/dist/js/create_sales_auto.js`
- `apps/business_app/serializers/sell_group.py` (`SellGroupSerializer._warehouse_report_lines`)
- Referencia (no se modifica): `templates/sales_products/salescar.html`,
  `static/assets/dist/js/salescar.js`
