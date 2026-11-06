# Spec 5 — Migrar a Django 6.1 reemplazando drf-extensions

- Issue: #5 — Migrar a Django 6.1 reemplazando drf-extensions
- Rama: `1-update-package-instalations`
- Estado: plan pendiente de aprobación

## Goal

Actualizar el proyecto a Django 6.1.x eliminando la dependencia incompatible
`drf-extensions`.

## User Story

Como mantenedor quiero usar Django 6.1 con una base de dependencias compatible para
mantener el framework al día sin romper endpoints.

## Requirements (EARS)

1. **When** el proyecto resuelva dependencias con `uv`, **the system shall** poder
   instalar Django 6.1.x sin conflictos.
2. **Where** se usa `rest_framework_extensions.routers.ExtendedSimpleRouter`, **the system
   shall** reemplazarlo por un router compatible con Django 6.1.
3. **When** se actualice el lockfile, **the system shall** excluir `drf-extensions`.
4. **The system shall** mantener las rutas `business-gestion/` funcionalmente equivalentes.
5. **The system shall** actualizar documentación interna con versiones efectivas de stack.

## Acceptance Criteria

1. [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml)
   usa Django 6.1.x.
2. `drf-extensions` deja de estar en
   [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml)
   y [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock).
3. [apps/business_app/urls.py](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/apps/business_app/urls.py)
   ya no importa `ExtendedSimpleRouter`.
4. `uv sync --frozen` y `uv run python manage.py check` pasan.
5. Test dirigido de humo en `business_app` pasa.

## Out of Scope

- Rediseñar jerarquías de rutas más allá del reemplazo necesario.
- Migraciones funcionales de negocio no relacionadas con compatibilidad.

## Affected Entities

- [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml)
- [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock)
- [apps/business_app/urls.py](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/apps/business_app/urls.py)
- [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
