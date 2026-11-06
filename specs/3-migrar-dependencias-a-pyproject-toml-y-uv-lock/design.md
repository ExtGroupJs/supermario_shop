# Design 3 — Migrar dependencias a pyproject.toml y uv.lock

## Contexto

Actualmente las dependencias se definen en:

- [requirements.txt](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/requirements.txt)
- [deploy_requirements.txt](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/deploy_requirements.txt)

El objetivo es adoptar el estándar de `uv`: `pyproject.toml` + `uv.lock` + `uv sync`.

## Approach

1. Crear [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml)
   con:
   - metadatos mínimos de proyecto (`name`, `version`, `requires-python`)
   - `dependencies` con todas las dependencias actuales
   - `optional-dependencies.deploy` para `gunicorn`
2. Generar [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock)
   con `uv lock`.
3. Cambiar instalación local a `uv sync`.
4. Cambiar instalación de despliegue a `uv sync --extra deploy`.
5. Eliminar archivos `requirements*.txt`.

## Justificación de `extra deploy`

`gunicorn` hoy se añade solo para despliegue. Mantenerlo en un extra evita cargar
dependencias de producción en todas las instalaciones locales.

## Cambios por archivo

1. Nuevo [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml).
2. Nuevo [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock).
3. Actualizar [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md)
   a `uv sync`.
4. Actualizar
   [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md)
   a `uv sync --extra deploy`.
5. Actualizar [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
   para que su setup y CI usen `uv sync`.
6. Actualizar
   [.github/workflows/django.yml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/.github/workflows/django.yml)
   para ejecutar `uv sync --extra deploy` en el servidor.
7. Eliminar [requirements.txt](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/requirements.txt)
   y
   [deploy_requirements.txt](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/deploy_requirements.txt).

## Verificación

1. `uv lock` ejecuta sin error.
2. `uv sync` ejecuta sin error.
3. `ruff check .` pasa.
4. `rg "requirements\\.txt|deploy_requirements\\.txt|uv pip install -r|pip install -r"` en
   superficies operativas no devuelve coincidencias no históricas.
