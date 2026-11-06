# Spec 2 — Migrar instalación de dependencias de pip a uv

- Issue: #2 — Migrar instalación de dependencias de pip a uv
- Rama: `1-update-package-instalations`
- Estado: plan pendiente de aprobación

## Goal

Usar `uv` como gestor de instalación de dependencias del proyecto en lugar de `pip`,
manteniendo el flujo actual basado en `requirements.txt` y `deploy_requirements.txt`.

## User Story

Como mantenedor del proyecto quiero que las instrucciones y automatizaciones instalen
dependencias con `uv`, para unificar el entorno de instalación y reducir el uso directo
de `pip`.

## Requirements (EARS)

1. **When** un desarrollador siga la guía local, **the system shall** indicar un flujo
   de instalación con `uv` y no con `pip install`.
2. **When** se documente el despliegue, **the system shall** usar comandos con `uv` para
   instalar dependencias desde los mismos archivos de requisitos.
3. **When** se ejecute el workflow de despliegue en GitHub Actions, **the system shall**
   invocar instalación de dependencias con `uv` en el servidor remoto.
4. **Where** exista referencia operativa a instalación con `pip install -r ...`,
   **the system shall** reemplazarla por el comando equivalente con `uv`.
5. **The system shall** preservar el resto del comportamiento del proyecto (migraciones,
   collectstatic, tests y lint) sin cambios funcionales.

## Acceptance Criteria

1. [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md)
   y [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
   ya no muestran `pip install -r requirements.txt` en sus flujos principales.
2. [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md)
   ya no muestra `pip install -r deploy_requirements.txt`.
3. [.github/workflows/django.yml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/.github/workflows/django.yml)
   reemplaza `pip install -r requirements.txt` por su equivalente con `uv`.
4. Una búsqueda global de `pip install -r` en el repositorio no devuelve resultados en
   flujos activos.
5. `ruff check .` continúa pasando.

## Out of Scope

- Migrar dependencias a `pyproject.toml`.
- Introducir `uv.lock` como requisito obligatorio del flujo.
- Cambiar la lógica de negocio o endpoints.
- Reestructurar Docker o infraestructura no relacionada con instalación de paquetes.

## Business Rules / Constraints

- Se mantiene el uso de `requirements.txt` y `deploy_requirements.txt` como fuente de
  dependencias en esta iteración.
- Los cambios deben ser documentales/operativos y no alterar comportamiento de runtime.

## Affected Entities

- [.github/workflows/django.yml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/.github/workflows/django.yml)
- [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md)
- [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md)
- [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
