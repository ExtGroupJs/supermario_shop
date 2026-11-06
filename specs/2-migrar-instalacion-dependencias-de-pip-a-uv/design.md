# Design 2 — Migrar instalación de dependencias de pip a uv

## Contexto actual

La instalación de dependencias aparece con `pip install` en:

- [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md)
- [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md)
- [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
- [.github/workflows/django.yml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/.github/workflows/django.yml)

El proyecto no requiere en este alcance migrar a `pyproject.toml`; por lo tanto se
mantiene instalación desde archivos requirements usando `uv pip`.

## Approach

Aplicar cambios quirúrgicos de comandos:

- Reemplazar `pip install -r requirements.txt` por
  `uv pip install -r requirements.txt`.
- Reemplazar `pip install -r deploy_requirements.txt` por
  `uv pip install -r deploy_requirements.txt`.
- En flujos de bootstrap, reemplazar `python -m venv venv` por `uv venv` cuando aplique
  el ejemplo principal de creación de entorno.

No se cambia estructura de dependencias ni código Python de la aplicación.

## Cambios por archivo

1. [README.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README.md)
   - Ajustar comandos de creación de entorno e instalación.
2. [README_for_deployment.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/README_for_deployment.md)
   - Ajustar comando de instalación de dependencias de despliegue.
3. [AGENTS.md](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/AGENTS.md)
   - Sincronizar la sección de setup local y nota de CI/deploy con `uv`.
4. [.github/workflows/django.yml](/home/ealmeida/Trabajo/Working_now/ExtGroupJs/code/el_punto/.github/workflows/django.yml)
   - Cambiar la instalación remota en el comando SSH para usar `uv pip`.

## Verificación

1. Búsqueda global de `pip install -r` debe quedar vacía en rutas operativas.
2. Ejecutar `ruff check .` para validar que no se rompe calidad base.
3. Confirmar que los cambios son solo de documentación/workflow.

## Riesgos y mitigación

- **Riesgo:** servidor de despliegue sin `uv`.
  - **Mitigación:** dejar explícito el requisito de `uv` en documentación.
- **Riesgo:** inconsistencia entre docs y workflow.
  - **Mitigación:** actualizar todas las superficies encontradas en una sola iteración.
