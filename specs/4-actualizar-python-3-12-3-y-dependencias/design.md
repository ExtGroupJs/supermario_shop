# Design 4 — Actualizar Python 3.12.3 y dependencias

## Decisiones de alcance confirmadas

- Python 3.11 se reemplaza; el proyecto queda solo en Python 3.12.x.
- Se permiten actualizaciones major de dependencias si la resolución es compatible.

## Enfoque técnico

1. Restringir runtime en [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml)
   a `>=3.12,<3.13`.
2. Actualizar dependencias directas con `uv`:
   - Ejecutar `uv lock --upgrade` para resolver últimas versiones compatibles.
   - Si alguna dependencia rompe, fijar pin mínimo necesario y documentar bloqueo.
3. Validar instalación reproducible con `uv sync --frozen`.
4. Actualizar documentación operativa de Python 3.11 a 3.12.3 en:
   - [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md)
   - [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md)
   - [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
5. Si cambios de dependencias introducen incompatibilidades visibles, correr una prueba
   dirigida de humo sobre Django:
   - `uv run python manage.py check`
   - `uv run pytest apps/business_app/tests/ -q` (solo si el check de Django pasa y hay
     tiempo razonable de ejecución).

## Riesgos y mitigación

- **Riesgo:** ruptura por cambios major de Django/DRF.
  - **Mitigación:** ejecutar validación de framework (`manage.py check`) y tests
    dirigidos; si falla, fijar versión compatible más alta alcanzable.
- **Riesgo:** conflictos transitivos en lock.
  - **Mitigación:** mantener cambios en dependencias directas y dejar que `uv` resuelva
    transitivas; no editar [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock) manualmente.

## Validación objetivo

- `uv lock --upgrade`
- `uv sync --frozen`
- `uv run python manage.py check`
- `ruff check .` (solo reporte: existe deuda histórica conocida)
