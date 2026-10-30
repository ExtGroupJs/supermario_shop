# Tasks 338 — Conditional dashboard showing

## Pre-requisitos

- [x] Issue #338 existe y esta asignado a `ealmeida1225`
- [x] Rama `338-conditional-dashboard-showing` activa
- [x] Decisiones cerradas: geo-IP por API HTTP + cache Django; fallback
      fail-closed (redirige a login); alcance `/`, `/catalog/`,
      `/wholesale_catalog/`
- [x] Proveedor elegido: `api.country.is` (`ipapi.co` dio `RateLimited` en
      pruebas reales)

## Tests first

- [x] T1. Crear `apps/common/utils/test_geo.py` con los casos del design
      (`settings.CACHES` a `LocMemCache` via fixture + `patch` de
      `requests.get`).
- [x] T2. Crear `apps/users_app/test_pages.py` con la tabla de casos del
      design (`monkeypatch` de `pages.get_country_code`).
- [x] T3. Ejecutar ambos ficheros y confirmar rojo antes de implementar.

## Implementacion

- [x] T4. Crear `apps/common/utils/geo.py`: `GEOIP_URL`, `GEOIP_TIMEOUT`,
      `GEOIP_HIT_TIMEOUT`, `GEOIP_MISS_TIMEOUT`, `get_client_ip()`,
      `get_country_code()` con cache 24h exito / 5min fallo y comentario
      `shortcut:` sobre proxies/VPN.
- [x] T5. En `apps/users_app/views/pages.py` importar `wraps` y
      `get_country_code`, definir `CUBA = "CU"` y el decorador
      `catalog_visible`.
- [x] T6. Decorar `catalog`, `root_catalog` y `wholesale_catalog` con
      `@catalog_visible`. **No** decorar `catalog_by_shop`.
- [x] T7. Ejecutar T1+T2: 24 passed.

## Verificacion

- [x] T8. `pytest apps/users_app/ apps/common/` → 46 passed.
- [x] T9. `ruff check` sobre los 4 ficheros → All checks passed.
- [x] T10. Revision manual con `runserver` e `X-Forwarded-For` simulado:
      - `152.206.0.1` (CU): `/`, `/catalog/`, `/wholesale_catalog/` → 302 a
        `/login/`
      - `8.8.8.8` (US): los tres → 200
      - `/catalogo/tienda/test/` con IP cubana → 200
- [x] T11. `makemigrations --check --dry-run` → No changes detected.
- [x] T12. Suite completa `pytest` → 221 passed.

## Notas de revision

- Sin modelos, serializers, viewsets ni templates: 2 ficheros de codigo +
  2 de test + specs.
- En `DEBUG=True` la cache es `DummyCache`, asi que en local cada peticion
  llama al servicio de geo-IP; es esperado.
- `ipapi.co` fue descartado: devolvio `RateLimited` desde la IP del servidor.
  `api.country.is` no limito 20 peticiones seguidas y resolvio CU correctamente.

## Aprobacion

- [x] Aprobacion explicita del `tasks.md` recibida del usuario antes de
      implementar (paso 6 del flujo SDD en `AGENTS.md`).
