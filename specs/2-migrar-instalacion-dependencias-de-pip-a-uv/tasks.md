# Tasks 2 — Migrar instalación de dependencias de pip a uv

## Pre-requisitos

- [x] Issue #2 creada.
- [x] Rama de trabajo activa y distinta de `main`/`dev`.
- [x] Superficies con `pip install` identificadas.

## Implementación

- [x] T1. Actualizar [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md)
      para usar comandos de `uv` en setup e instalación.
- [x] T2. Actualizar
      [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md)
      para usar `uv pip install -r deploy_requirements.txt`.
- [x] T3. Actualizar [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
      para alinear setup local y nota de CI/deploy con `uv`.
- [x] T4. Actualizar
      [.github/workflows/django.yml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/.github/workflows/django.yml)
      para instalar dependencias remotas con `uv`.

## Verificación

- [x] V1. Ejecutar búsqueda global y confirmar que no quedan coincidencias operativas de
      `pip install -r`.
- [x] V2. Ejecutar `ruff check .`.
- [x] V3. Revisar que no se tocaron módulos de negocio ni lógica de API.

## Aprobación

- [x] Aprobación explícita del usuario para este `tasks.md` antes de implementar
      (paso 6 del flujo SDD en [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)).
