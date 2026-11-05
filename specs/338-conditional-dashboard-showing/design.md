# Design 338 — Conditional dashboard showing

## Approach

Un decorador de vista + un helper de geo-IP. Nada mas: no hay modelo, no hay
middleware, no hay template nuevo.

Regla unica: `allow = user.is_authenticated or country in FOREIGN`.
`country` vacio (servicio caido, IP privada, respuesta invalida) cae del lado
bloqueado, como se decidió (fail-closed).

## Existing patterns reused

- `apps/users_app/views/pages.py` ya envuelve vistas con decoradores
  (`@user_passes_test(is_owner)`) y ya comparte contexto con
  `_get_catalog_context()`.
- `from django.shortcuts import redirect, render` ya esta importado en ese
  fichero.
- `requests` 2.32.3 ya esta instalado (`requirements.txt`); no se añade
  dependencia.
- Cache de Django (`CACHES["default"]`) ya configurada en
  `project_site/settings.py` (`DummyCache` en DEBUG, Redis en produccion).
- Tests de paginas: `apps/users_app/test_commands_and_flow.py` usa el `client`
  fixture de pytest-django; se sigue ese patrón.

## Changes

### 1) New: `apps/common/utils/geo.py`

```python
GEOIP_URL = "https://api.country.is/{ip}"
GEOIP_TIMEOUT = 2
GEOIP_HIT_TIMEOUT = 60 * 60 * 24
GEOIP_MISS_TIMEOUT = 60 * 5

def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "").strip()

def get_country_code(request):
    """Country ISO code for the request IP; "" when unknown (fail-closed)."""
    ip = get_client_ip(request)
    if not ip:
        return ""
    key = f"geoip:{ip}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    try:
        response = requests.get(GEOIP_URL.format(ip=ip), timeout=GEOIP_TIMEOUT)
        code = str(response.json()["country"]).strip().upper()
        valid = bool(response.ok and len(code) == 2 and code.isalpha())
    except (requests.RequestException, ValueError, KeyError, TypeError):
        valid, code = False, ""
    cache.set(key, code, GEOIP_HIT_TIMEOUT if valid else GEOIP_MISS_TIMEOUT)
    return code if valid else ""
```

- Motivo del cambio de proveedor: `ipapi.co` respondio `RateLimited` en pruebas
  reales desde la IP de desarrollo; `api.country.is` aguanto 20 peticiones
  seguidas sin limite y resolvio IPs cubanas (`152.206.0.1` → `CU`).
- `response.ok` se comprueba: un 4xx con JSON de error no debe leerse como pais.

- `shortcut: cache does not know proxies/VPNs, upgrade to a local MaxMind DB
  only if false positives matter.`
- Cache con dos TTL: exito 24h, fallo 5min, para no martillar el servicio
  cuando esta caido.

### 2) `apps/users_app/views/pages.py`

```python
from functools import wraps
from apps.common.utils.geo import get_country_code

CUBA = "CU"

def catalog_visible(view):
    """Show public catalog to logged users and foreign visitors only."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        # Logged users skip the geo-IP lookup entirely (no latency per page).
        if not request.user.is_authenticated:
            country = get_country_code(request)
            if country in ("", CUBA):
                return redirect("first_login")
        return view(request, *args, **kwargs)
    return wrapper
```

Decorar exactamente tres vistas:

```python
@catalog_visible
def catalog(request): ...

@catalog_visible
def wholesale_catalog(request): ...
```

`root_catalog` tambien recibe el decorador aunque hoy no esta enrutada
(regla de negocio identica si se monta despues).

`catalog_by_shop` **no** se decora (fuera de alcance).

### 3) `project_site/urls.py` — sin cambios

Rutas afectadas de facto:

| URL | Vista |
| --- | --- |
| `/` | `pages.wholesale_catalog` |
| `/wholesale_catalog/` | `pages.wholesale_catalog` |
| `/catalog/` | `pages.catalog` (primera regla gana sobre la de `catalogo`) |

## Tests

### `apps/common/utils/test_geo.py` (nuevo)

`override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})`:

1. IP extranjera (`8.8.8.8`) + `requests.get` mockeado devolviendo `"US"` →
   `get_country_code` devuelve `"US"`.
2. Segunda llamada con la misma IP no vuelve a invocar `requests.get`
   (contador de llamadas == 1).
3. `requests.get` lanza `Timeout` → `""`.
4. Respuesta `200` con cuerpo raro (`"N/A"`) → `""`.
5. `X-Forwarded-For: 8.8.8.8, 10.0.0.1` → se usa solo la primera IP.

Se mockea `apps.common.utils.geo.requests.get` con
`unittest.mock.patch`.

### `apps/users_app/test_pages.py` (nuevo)

`monkeypatch.setattr(pages, "get_country_code", lambda request: code)`:

| Caso | Esperado |
| --- | --- |
| anon + `"US"` + `/` | `200`, usa template `catalogo_por_mayor/catalogo_por_mayor.html` |
| anon + `"CU"` + `/` | `302` a `/login/` |
| anon + `""` (desconocido) + `/` | `302` a `/login/` |
| anon + `"CU"` + `/catalog/` | `302` a `/login/` |
| anon + `"CU"` + `/wholesale_catalog/` | `302` a `/login/` |
| login + `"CU"` + `/` | `200` |
| login + `""` + `/catalog/` | `200` |
| anon + `"CU"` + `/catalogo/tienda/<slug>/` | `200` (fuera de alcance) |

Para el login se usa `baker.make(SystemUser)` + `client.force_login(user)`,
patrón ya usado en `BaseTestClass`.

## Risks / notes

- En local (`DEBUG=True`) la cache es `DummyCache`: sin cache real, cada
  peticion llama al servicio. En produccion (Redis) se cachea 24h por IP de
  cliente.
- IPs privadas/localhost (`127.0.0.1`) devolveran `""` → bloqueo. En desarrollo
  la raiz redirige a login; es el comportamiento fail-closed acordado.
  (`api.country.is` responde `{"error": "private range"}` para IPs privadas, que
  cae en el except y se trata como desconocido.)
- nginx ya pasa `X-Forwarded-For` via `proxy_params` (ver
  `README_for_deployment.md`), asi que la IP real se obtiene sin tocar
  infraestructura.
- No hay indice de cache de `CGI`/Cloudflare: si algun dia se mete un CDN, la
  cabecera correcta seria `CF-IPCountry` y habria que priorizarla.
