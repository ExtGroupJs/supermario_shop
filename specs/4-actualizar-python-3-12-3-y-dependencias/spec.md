# Spec 4 — Actualizar Python 3.12.3 y dependencias

- Issue: #4 — Actualizar proyecto a Python 3.12.3 y dependencias compatibles
- Rama: `1-update-package-instalations`
- Estado: plan pendiente de aprobación

## Goal

Actualizar el proyecto para trabajar con Python 3.12.3 como versión soportada y subir
dependencias (incluyendo Django/DRF y mayores cuando sean compatibles) usando `uv`.

## User Story

Como desarrollador quiero usar Python 3.12.3 y versiones recientes de dependencias para
reducir deuda técnica y mantener compatibilidad del proyecto.

## Requirements (EARS)

1. **When** se configure el entorno local, **the system shall** usar Python 3.12.3 en
   comandos de setup documentados.
2. **When** se resuelvan dependencias con `uv`, **the system shall** actualizar versiones
   de paquetes a las más recientes compatibles, incluyendo actualizaciones major.
3. **When** se defina compatibilidad de runtime, **the system shall** reemplazar el rango
   previo y dejar soporte solo para Python 3.12.x.
4. **Where** el proyecto declare versiones de framework en documentación interna,
   **the system shall** reflejar las nuevas versiones efectivas.
5. **The system shall** regenerar `uv.lock` a partir del `pyproject.toml` actualizado.

## Acceptance Criteria

1. [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml)
   define soporte de runtime restringido a Python 3.12.x.
2. Dependencias clave (`Django`, `djangorestframework` y demás posibles) quedan
   actualizadas en [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml)
   sin conflictos de resolución.
3. [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock)
   queda regenerado acorde a las nuevas versiones.
4. [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md),
   [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md)
   y [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
   reflejan Python 3.12.3.
5. Validaciones ejecutadas y reportadas: `uv lock`, `uv sync --frozen`, tests
   dirigidos relevantes y `ruff check .`.

## Out of Scope

- Reescritura funcional de negocio fuera de ajustes necesarios por incompatibilidades.
- Cambios de infraestructura no relacionados con versión de Python/dependencias.

## Compatibility Notes

- Se revisará guía oficial de compatibilidad de Python 3.12:
  https://docs.python.org/3.12/whatsnew/3.12.html

## Affected Entities

- [pyproject.toml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/pyproject.toml)
- [uv.lock](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/uv.lock)
- [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md)
- [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md)
- [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
