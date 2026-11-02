# Design 341 — Omitir la acción Borrar del listado de grupos de venta

## Cause

`static/assets/dist/js/group_sells.js` renderiza un botón **Borrar** en la columna
**Acciones** y su manejador llama a:

```text
DELETE /business-gestion/group-sells/<id>/
```

Sin embargo, `apps/business_app/views/group_sell.py` define `GroupSellViewSet` solo con
`RetrieveModelMixin` y `ListModelMixin`. El router de DRF no genera una ruta `destroy`,
por lo que esa petición responde `405 Method Not Allowed`.

`apps/business_app/views/sell_group.py` sí incluye `DestroyModelMixin`, pero corresponde
a otro flujo (`/business-gestion/sell-groups/`). La acción actual usa por error el
recurso de solo lectura.

## Approach

Eliminar la acción no soportada de extremo a extremo. No se añade un método `DELETE` ni
se cambia el comportamiento de la API: la incidencia pide omitir **Borrar** del listado.

## Existing patterns reused

- Se conserva la columna **Acciones** y sus demás controles en
  `static/assets/dist/js/group_sells.js`.
- Se conserva la vista `group_sells` y su renderizado en
  `apps/users_app/views/pages.py`.
- Se agregan las comprobaciones de regresión al fichero existente
  `apps/business_app/tests/group_sells/test_group_sells_functionalities.py`, que ya
  carga la página y valida la integración entre su HTML y el endpoint.

## Changes

### 1) `static/assets/dist/js/group_sells.js`

- Quitar de la columna **Acciones** el botón condicional **Borrar**, incluido el
  `onclick` que invoca `deleteGroupSell`.
- Eliminar `deleteGroupSell`, ya que no quedará ningún llamador.
- Mantener intactas las acciones de detalle, comprobante, preventa y venta.

### 2) `templates/sales/group_sells.html`

- Eliminar el bloque que asigna `window.canDeleteGroupSell`; ese flag solo existía
  para controlar el botón retirado.

### 3) `apps/users_app/views/pages.py`

- Eliminar el cálculo de `can_delete` y el contexto `can_delete_group` de la vista
  `group_sells`.
- Mantener el resto de la vista y del import de `Groups`, que sigue usándose por
  `is_owner`.

### 4) `apps/business_app/tests/group_sells/test_group_sells_functionalities.py`

Añadir una regresión pequeña que:

1. inicia sesión con `SHOP_OWNER` (el rol que antes recibía el botón);
2. carga `/business-gestion/group-sells/`;
3. comprueba que la plantilla no contiene `canDeleteGroupSell`;
4. comprueba que el contexto no contiene `can_delete_group`;
5. lee `static/assets/dist/js/group_sells.js` y comprueba que ya no contiene
   `deleteGroupSell` ni la etiqueta **Borrar**.

La prueba inspecciona el asset servido por la propia aplicación porque la acción se
construye en JavaScript y no aparece en el HTML renderizado.

## API impact

Ninguno. `GroupSellViewSet` continúa siendo de solo lectura y `DELETE` sobre
`group-sells` continúa respondiendo `405`, como exige el alcance de la incidencia.

## Risks / notes

- No se elimina ni modifica `SellGroupViewSet`; el flujo de borrado existente en
  `/business-gestion/sell-groups/` permanece intacto.
- Los navegadores que tengan la versión anterior del JavaScript en caché podrían
  intentar el `DELETE` hasta que se renueve el asset desplegado; el backend ya lo
  rechaza con `405` y no se modifican datos.
