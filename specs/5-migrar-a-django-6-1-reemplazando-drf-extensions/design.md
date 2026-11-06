# Design 5 — Migrar a Django 6.1 reemplazando drf-extensions

## Evidencia actual

- `drf-extensions` se usa solo en
  [apps/business_app/urls.py](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/apps/business_app/urls.py)
  vía `ExtendedSimpleRouter`.
- No hay otras importaciones de `rest_framework_extensions` en el código Python.
- El archivo no define nested routes; solo hace múltiples `router.register(...)`.

## Estrategia

1. Reemplazar `ExtendedSimpleRouter` por `SimpleRouter` de DRF en
   [apps/business_app/urls.py](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/apps/business_app/urls.py).
2. Eliminar `drf-extensions` de dependencias y resolver con `uv`.
3. Intentar Django 6.1.x; si resolución y checks pasan, mantenerlo.
4. No introducir `drf-nested-routers` salvo que el reemplazo simple falle, porque hoy no
   hay enrutado anidado en uso.

## Cambios previstos

- [apps/business_app/urls.py](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/apps/business_app/urls.py):
  cambio de import y clase de router.
- [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml):
  quitar `drf-extensions`, fijar Django 6.1.x.
- [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock):
  regenerar.
- [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md):
  actualizar nota de stack y de router usado en `business_app`.

## Validación

- `uv lock --upgrade`
- `uv sync --frozen`
- `uv run python manage.py check` (con `.env` temporal)
- `uv run pytest -q apps/business_app/tests/group_sells/test_group_sells_functionalities.py`
