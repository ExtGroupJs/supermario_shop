# Spec 341 — Omitir la acción Borrar del listado de grupos de venta

- Issue: #341 — Delete method not allowed for business-gestion/group-sells
- Rama: `341-delete-method-not-allowed-for-business-gestiongroup-sells`
- Estado: plan pendiente de aprobación

## Goal

Evitar que la pantalla de grupos de venta ofrezca una acción **Borrar** que no puede
funcionar. El listado consume `GET /business-gestion/group-sells/`, un recurso de solo
lectura; por ello `DELETE /business-gestion/group-sells/<id>/` responde `405 Method Not
Allowed`.

## User Story

Como usuario del negocio quiero que el listado de grupos de venta solo muestre acciones
que el backend admite, para no recibir errores al intentar eliminar una venta.

## Requirements

1. Cuando se renderice el listado de grupos de venta, la columna **Acciones** no deberá
   incluir un control **Borrar** para ningún rol.
2. Cuando se cargue el listado de grupos de venta, el frontend no deberá intentar
   ejecutar `DELETE` contra `/business-gestion/group-sells/<id>/`.
3. Cuando se renderice el listado de grupos de venta, no se deberá exponer una señal de
   permisos específica para la acción eliminada.
4. Las demás acciones del listado y el comportamiento de lectura de
   `/business-gestion/group-sells/` deberán permanecer sin cambios.
5. El endpoint `DELETE /business-gestion/group-sells/<id>/` deberá continuar sin soporte;
   esta incidencia corrige la interfaz, no amplía la API.

## Acceptance Criteria

1. Al abrir `/business-gestion/group-sells/` como `SUPER_ADMIN`, `SHOP_OWNER` o
   `SHOP_SELLER`, la columna **Acciones** no muestra **Borrar**.
2. El JavaScript del listado no contiene el manejador de eliminación ni construye una
   petición `DELETE` hacia `group-sells`.
3. La plantilla del listado no expone `window.canDeleteGroupSell` ni el contexto
   `can_delete_group`.
4. Las acciones existentes (detalle, comprobante y creación de preventa/venta) siguen
   presentes.
5. `GET /business-gestion/group-sells/` continúa devolviendo el listado y
   `DELETE /business-gestion/group-sells/<id>/` continúa respondiendo `405`.

## Out of Scope

- Añadir `DestroyModelMixin` o cualquier otro soporte `DELETE` a `GroupSellViewSet`.
- Redirigir la acción **Borrar** hacia `/business-gestion/sell-groups/<id>/`.
- Cambiar el flujo de cancelación de ventas existente.
- Rediseñar las demás acciones o el resto del listado.

## Business Rules / Permissions

- `GroupSellViewSet` es intencionadamente de solo lectura: crear y cancelar ventas se
  administra mediante los endpoints de grupos y productos de venta.
- Ningún rol puede eliminar un grupo desde este listado, incluidos `SUPER_ADMIN` y
  `SHOP_OWNER`.
- La、画面 de acciones debe reflejar únicamente operaciones admitidas por el recurso
  que consume.

## Affected Entities

- Frontend: `static/assets/dist/js/group_sells.js`.
- Plantilla: `templates/sales/group_sells.html`.
- Vista de página: `apps/users_app/views/pages.py`.
- Tests: `apps/business_app/tests/group_sells/test_group_sells_functionalities.py`.
- Sin cambios en modelos, serializers, viewsets de API, permisos ni rutas.
