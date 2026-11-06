# Tasks 5 — Migrar a Django 6.1 reemplazando drf-extensions

## Pre-requisitos

- [x] Issue #5 creada.
- [x] Uso de `drf-extensions` localizado y acotado.

## Implementación

- [x] T1. Reemplazar `ExtendedSimpleRouter` por `SimpleRouter` en
      [apps/business_app/urls.py](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/apps/business_app/urls.py).
- [x] T2. Actualizar
      [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml)
      para quitar `drf-extensions` y fijar Django 6.1.x.
- [x] T3. Regenerar [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock)
      con `uv lock --upgrade`.
- [x] T4. Actualizar texto de stack/router en
      [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md).
- [x] T5. Ajustar
      [pytest.ini](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pytest.ini)
      para warning class deprecada tras Django 6.1 (`RemovedInDjango70Warning`).

## Verificación

- [x] V1. `uv sync --frozen` exitoso.
- [x] V2. `uv run python manage.py check` exitoso.
- [x] V3. `uv run pytest -q apps/business_app/tests/group_sells/test_group_sells_functionalities.py` exitoso.

## Aprobación

- [x] Aprobación explícita del usuario para implementar este plan.
