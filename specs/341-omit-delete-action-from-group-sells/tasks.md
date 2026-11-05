# Tasks 341 — Omitir la acción Borrar del listado de grupos de venta

## Pre-requisitos

- [x] Issue #341 existe.
- [x] Rama `341-delete-method-not-allowed-for-business-gestiongroup-sells` activa.
- [x] Verificado que `GroupSellViewSet` solo admite listar y recuperar; por eso
      `DELETE /business-gestion/group-sells/<id>/` responde `405`.
- [x] Alcance aprobado por el usuario: omitir **Borrar** del listado, sin añadir soporte
      `DELETE` a la API.

## Tests first

- [ ] T1. Añadir en
      `apps/business_app/tests/group_sells/test_group_sells_functionalities.py` una
      regresión para `SHOP_OWNER` que compruebe que la página no expone
      `canDeleteGroupSell`, el contexto no expone `can_delete_group` y el JavaScript no
      contiene `deleteGroupSell` ni **Borrar**.
- [ ] T2. Ejecutar el test nuevo y confirmar que falla antes de la implementación.

## Implementación

- [ ] T3. En `static/assets/dist/js/group_sells.js`, quitar el botón **Borrar** de la
      columna **Acciones** y eliminar el manejador `deleteGroupSell` sin tocar las demás
      acciones.
- [ ] T4. En `templates/sales/group_sells.html`, quitar la asignación de
      `window.canDeleteGroupSell`.
- [ ] T5. En `apps/users_app/views/pages.py`, quitar `can_delete` y
      `can_delete_group` de la vista `group_sells`.
- [ ] T6. Ejecutar el test de T1 y confirmar que pasa.

## Verificación

- [ ] T7. Ejecutar
      `pytest apps/business_app/tests/group_sells/test_group_sells_functionalities.py`.
- [ ] T8. Ejecutar `ruff check .`.
- [ ] T9. Revisar el diff final: sin cambios en modelos, API, permisos o rutas, y con las
      demás acciones del listado intactas.

## Aprobación

- [ ] Aprobación explícita del usuario para este `tasks.md` antes de implementar
      (paso 6 del flujo SDD de `AGENTS.md`).
