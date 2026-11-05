# Spec 338 — Conditional dashboard showing

- Issue: #338 — Conditional dashboard showing
- Rama: `338-conditional-dashboard-showing`
- Estado: plan pendiente de aprobacion

## Goal

Ocultar las paginas publicas de catalogo a los visitantes anonimos que entran
desde Cuba, mostrandolas solo a usuarios autenticados o a visitantes de otro
pais.

## User Story

Como responsable del negocio quiero que un visitante cubano sin sesion no pueda
ver los catalogos publicos (`/`, `/catalog/`, `/wholesale_catalog/`), mientras
que un cliente en el exterior o cualquier usuario autenticado sigue entrando
normalmente.

## Requirements

1. Un usuario autenticado siempre puede ver las paginas de catalogo.
2. Un visitante anonimo cuyo pais de origen no es Cuba puede verlas.
3. Un visitante anonimo desde Cuba (o con pais indeterminable) es redirigido a
   la pagina de login.
4. El pais se resuelve por la IP del cliente (cabecera `X-Forwarded-For` que ya
   pone nginx, con fallback a `REMOTE_ADDR`) mediante un servicio HTTP de
   geo-IP, con cache de 24h por IP.
5. Un fallo del servicio de geo-IP no debe romper la pagina: se trata como
   "no autorizado" (fail-closed) y se cachea el fallo solo 5 minutos.
6. Nada de esto cambia el comportamiento de `catalogo/tienda/<slug:>/` ni de
   las APIs de catalogo.

## Acceptance Criteria

1. `GET /` anonimo, pais distinto de CU → `200` con el catalogo.
2. `GET /` anonimo, pais CU → `302` hacia `/login/`.
3. `GET /catalog/` y `GET /wholesale_catalog/` se comportan igual que 1 y 2.
4. `GET /` con sesion iniciada, pais CU → `200` (la sesion manda).
5. `GET /` anonimo con el servicio de geo-IP caido o respondiendo algo invalido
   → `302` hacia `/login/`.
6. El resultado del geo-IP se cachea por IP; una segunda peticion de la misma
   IP no vuelve a llamar al servicio.
7. `GET /catalogo/tienda/<slug>/` anonimo desde Cuba sigue devolviendo `200`.

## Out of Scope

- `catalogo/tienda/<slug:>/` (enlace por tienda, se comparte con clientes
  concretos).
- Endpoints de la API (`business-gestion/*`), que ya exigen autenticacion o son
  `AllowAny` deliberados.
- Resolver la duplicidad de rutas `catalog/` y del nombre `catalog` en
  `project_site/urls.py` (se documenta, no se corrige aqui).
- Software de geo-IP local (MaxMind), VPN/proxy detection, listas de paises
  permitidos distintas de Cuba.

## Business Rules / Permissions

- Regla de visibilidad: `authenticated OR country != "CU"`.
- Pais indeterminable se evalua como Cuba (fail-closed). Alternativa descartada:
  fail-open.
- La cache es la de Django (`CACHES["default"]`); en `DEBUG=True` es
  `DummyCache`, asi que no hay cache local, pero no hay riesgo de datos viejos
  en desarrollo.
- Servicio de geo-IP: `https://api.country.is/{ip}` (JSON
  `{"ip": ..., "country": "US"}`), timeout 2s, sin dependencia nueva
  (`requests` ya esta en `requirements.txt`). Descartado `ipapi.co`: en pruebas
  reales devolvio `RateLimited` desde la IP del servidor.

## Affected Entities

- Vista: `apps/users_app/views/pages.py` (`catalog`, `root_catalog`,
  `wholesale_catalog`).
- Rutas: `project_site/urls.py` (sin cambios, solo referencia).
- Tests: nuevo `apps/users_app/test_pages.py`.
- Sin migraciones, sin modelos, sin serializers, sin templates nuevos.
