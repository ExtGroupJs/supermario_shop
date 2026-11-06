# Tasks 3 — Migrar dependencias a pyproject.toml y uv.lock

## Pre-requisitos

- [x] Issue #3 creada.
- [x] Alcance confirmado: quitar `requirements*.txt` y usar estándar `uv` con TOML.

## Implementación

- [x] T1. Crear [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml)
      con dependencias actuales y extra `deploy`.
- [x] T2. Generar [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock)
      con `uv lock`.
- [x] T3. Actualizar [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md)
      para usar `uv sync`.
- [x] T4. Actualizar
      [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md)
      para usar `uv sync --extra deploy`.
- [x] T5. Actualizar [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
      para alinear setup/CI con `uv sync`.
- [x] T6. Actualizar
      [.github/workflows/django.yml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/.github/workflows/django.yml)
      para usar `uv sync --extra deploy`.
- [x] T7. Eliminar [requirements.txt](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/requirements.txt)
      y
      [deploy_requirements.txt](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/deploy_requirements.txt).

## Verificación

- [x] V1. Ejecutar `uv lock`.
- [x] V2. Ejecutar `uv sync`.
- [x] V3. Ejecutar `ruff check .` (falla por deuda técnica preexistente fuera del alcance).
- [x] V4. Verificar búsqueda global sin referencias operativas a `requirements*.txt` ni
      `pip install -r`.

## Aprobación

- [x] Aprobación explícita del usuario para este plan antes de implementar (flujo SDD).
