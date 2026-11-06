# Spec 3 — Migrar dependencias a pyproject.toml y uv.lock

- Issue: #3 — Migrar dependencias a pyproject.toml + uv.lock y retirar requirements.txt
- Rama: `1-update-package-instalations`
- Estado: plan pendiente de aprobación

## Goal

Eliminar la dependencia operativa de `requirements.txt`/`deploy_requirements.txt` y
adoptar el estándar de `uv` con `pyproject.toml` + `uv.lock`.

## User Story

Como mantenedor del proyecto quiero administrar dependencias con el flujo estándar de
`uv` para no mantener archivos `requirements*.txt` y tener instalaciones reproducibles
con `uv sync`.

## Requirements (EARS)

1. **When** un desarrollador prepare el entorno local, **the system shall** instalar
   dependencias desde `pyproject.toml` usando `uv sync`.
2. **When** se ejecute el flujo de despliegue, **the system shall** instalar
   dependencias con `uv sync` y sin `requirements*.txt`.
3. **Where** exista documentación de instalación, **the system shall** referenciar
   `pyproject.toml`/`uv.lock` como fuente de dependencias.
4. **The system shall** conservar las mismas dependencias funcionales ya presentes en
   `requirements.txt` y `deploy_requirements.txt`.
5. **The system shall** incluir un `uv.lock` versionado para instalaciones consistentes.

## Acceptance Criteria

1. Existe [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml)
   con `project.dependencies` equivalente al inventario actual de dependencias.
2. Existe [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock)
   generado por `uv`.
3. Ya no hay uso operativo de `requirements.txt` ni `deploy_requirements.txt` en:
   [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md),
   [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md),
   [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md),
   [.github/workflows/django.yml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/.github/workflows/django.yml).
4. `requirements.txt` y `deploy_requirements.txt` se eliminan del repositorio.
5. `ruff check .` continúa pasando.

## Out of Scope

- Cambiar versiones de librerías por modernización funcional.
- Reestructurar Docker/infra no relacionada con instalación.
- Cambiar lógica de negocio o de API.

## Business Rules / Constraints

- Mantener Python 3.11 como baseline del proyecto.
- No introducir abstracciones nuevas fuera de gestión de dependencias.

## Affected Entities

- [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml) (nuevo)
- [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock) (nuevo)
- [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md)
- [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md)
- [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
- [.github/workflows/django.yml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/.github/workflows/django.yml)
- [requirements.txt](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/requirements.txt) (eliminar)
- [deploy_requirements.txt](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/deploy_requirements.txt) (eliminar)
