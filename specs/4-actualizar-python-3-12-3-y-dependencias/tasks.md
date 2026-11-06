# Tasks 4 — Actualizar Python 3.12.3 y dependencias

## Pre-requisitos

- [x] Issue #4 creada.
- [x] Alcance confirmado por usuario: solo Python 3.12.x + updates major/minor/patch.

## Implementación

- [x] T1. Ajustar [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml)
      para declarar runtime `>=3.12,<3.13`.
- [x] T2. Actualizar dependencias directas a versiones recientes compatibles con Python
      3.12.x (incluyendo Django y DRF) usando `uv lock --upgrade`.
- [x] T3. Regenerar [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock)
      con la resolución final.
- [x] T4. Actualizar referencias de Python en
      [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md),
      [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md)
      y [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
      a 3.12.3.
- [x] T5. Actualizar encabezado de stack en
      [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
      con versiones reales de Django/DRF tras lock.

## Verificación

- [x] V1. `uv lock --upgrade` exitoso.
- [x] V2. `uv sync --frozen` exitoso.
- [x] V3. `uv run python manage.py check` exitoso.
- [x] V4. `ruff check .` ejecutado y resultado reportado (falla por deuda histórica no relacionada).

## Aprobación

- [x] Aprobación explícita del usuario para implementar este `tasks.md`.
