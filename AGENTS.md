# AGENTS.md

## Project

Django 5.1.1 + DRF 3.15.2 auto parts shop (Geely vehicles). Python 3.11. Session-based auth. Spanish locale (`es-es`). `USE_TZ = False`, timezone `America/Havana`.

## Codebase Knowledge Graph (codebase-memory-mcp)

This repo uses codebase-memory-mcp (local-first MCP server). A committed index snapshot lives in `.codebase-memory/graph.db.zst`; if it is stale or missing, run `codebase-memory-mcp cli index_repository --repo-path "$PWD" --mode full --persistence true` (or ask the user to run it in OpenCode).

ALWAYS use ENGLISH language for coding, including docstrings

ALWAYS prefer graph tools over grep/glob/file-search for structural questions:

1. `search_graph` — find functions, classes, routes, variables by pattern
2. `trace_path` — trace who calls a function or what it calls
3. `get_code_snippet` — read specific function/class source code
4. `check_index_coverage` — validate candidate paths / missed ranges before making claims
5. `query_graph` — Cypher queries for complex patterns
6. `get_architecture` — high-level project summary

Evidence tiers: **Scout** (quick positive lookups, mark provisional), **Verify** (default; task-directed evidence + exact snippets), **Auditor** (bounded full verification with coverage disclosure). After identifying candidate paths, call `check_index_coverage` once with each evidence path before relying on graph results; for partial/unknown coverage, read/grep the reported ranges directly.

Fall back to grep/glob for: string literals, error messages, config values, non-code files (Dockerfiles, shell scripts, fixtures, templates structure), and when graph tools return insufficient results. Series of calls that must run sequentially are the exception; batch independent graph calls in parallel.

## Local Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp REFERENCE.env .env        # set RUNNING_FROM=local for SQLite
python manage.py migrate
python manage.py create_test_users   # creates 300 dummy users
python manage.py runserver
```

Swagger UI: `http://127.0.0.1:8000/api/swagger/`

## Commands

```bash
pytest                              # run all tests
pytest apps/business_app/tests/     # run one app's tests
pytest path/to/test_file.py         # run single file
pytest -k "test_name"               # run single test

python manage.py load_data          # load initial fixtures (groups, brands, models, products)
python manage.py reset_data         # reset sells/quantities for dev
python manage.py create_new_shop    # seed Geely shop with products
python manage.py createsuperuser    # create admin user

ruff check .                        # lint (no ruff config file; uses defaults)
ruff check --fix .                  # auto-fix lint issues
```

## Architecture

```
project_site/       Django project settings, urls, wsgi
apps/
  common/           Shared: BaseModel, GenericLogMixin, pagination, middleware, filters, serializers, management commands
  business_app/     Core domain: Brand, Model, Product, Shop, ShopProducts, Sell, SellGroup, Dashboard
  users_app/        SystemUser, Groups (SUPER_ADMIN=1, SHOP_OWNER=2, SHOP_SELLER=3)
  clients_app/      Client management
templates/          HTML templates (server-rendered pages)
static/             Static assets (JS, CSS, images)
```

API routes (all under `business-gestion/`):
- `brands/`, `models/`, `products/`, `shops/`
- `shop-products/`, `shop-products-logs/`
- `sell-products/`, `sell-groups/`, `payment-methods/`
- `dashboard/`, `shop-product-input-group/`

User routes: `user-gestion/users/`, `user-gestion/groups/`
Common routes: `common/logs/`

## DRF Structure Standard

MANDATORY for any new feature/entity. Follow this layout exactly so the codebase stays uniform.

### Models

- One file per model under `<app>/models/<name>.py`, re-exported in `<app>/models/__init__.py`.
- Inherit `BaseModel` (`apps/common/models/base_model.py`) for `created_timestamp`/`updated_timestamp`. Use `models.Model` only for static/read-only entities.
- If audit-trail is needed, inherit `GenericLogMixin` FIRST (must be first parent — overrides `save`/`delete`), `SafeDeleteModel` second, `BaseModel` last:
  ```python
  class ShopProducts(GenericLogMixin, SafeDeleteModel, BaseModel):
      _safedelete_policy = SOFT_DELETE
  ```

### ViewSets

- One file per viewset under `<app>/views/<name>.py`.
- The file `<name>.py` must match the model filename.
- Full CRUD → `class XViewSet(SerializerMapMixin, viewsets.ModelViewSet, GenericAPIView)`. When update is not wanted, compose only needed mixins (e.g. `CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin` + `GenericViewSet`).
- Always declare all three filter backends:
  ```python
  filter_backends = [DjangoFilterBackend, filters.SearchFilter, CommonOrderingFilter]
  ```
- Default `CommonRolePermission` (or an app-specific subclass). `@action(detail=False, methods=["GET"], permission_classes=[AllowAny])` for public catalog-ish endpoints.
- Override `perform_create` to attach the actor: `serializer.save(seller=SystemUser.objects.get(id=self.request.user.id))`.
- Role-based row filtering goes in `get_queryset()` (see `shop_products.py`, `sell.py`).
- Pagination: `AllResultsSetPagination` when the endpoint must return everything (e.g. products); the default `StandardResultsSetPagination` otherwise.

### Serializers

- One file per model under `<app>/serializers/<name>.py`.
- The file `<name>.py` must match the model filename, if several serializers are needed, all of them should be on this file.
- Write serializer = flat `ModelSerializer` with FKs as bare PKs. Read serializer extends it, swapping FKs for nested read serializers:
  ```python
  class ReadProductSerializer(ProductSerializer):
      model = ReadModelSerializer()
      class Meta(ProductSerializer.Meta):
          fields = ProductSerializer.Meta.fields + ("id", "model_name", "__str__")
  ```
- Wire read serializers to the viewset with `SerializerMapMixin`: declare `list_serializer_class`, `retrieve_serializer_class`, etc. (`{action}_serializer_class`).
- Annotate extra columns (e.g. `model_name`) in the viewset `queryset` with `.annotate(...)`; add matching `read_only=True` fields in the read serializer.
- Parent+children payloads (SellGroup+sells, InputGroup+inputs) embed the child serializer with `many=True`; the view's `create()` pops children from `validated_data` and bulk-creates them.

### URLs

- Register each viewset in the app's `urls.py`. `business_app` uses `ExtendedSimpleRouter`; other apps use `routers.DefaultRouter`.
- Mount app routers in `project_site/urls.py` under their prefix (`business-gestion/`, `user-gestion/`, etc.).

## Key Patterns

- **GenericLogMixin**: Audit logging mixin. Must be **first** parent class (overrides `save`/`delete`). Use with `SafeDeleteModel` second.
- **BaseModel**: Provides `created_timestamp`/`updated_timestamp` — all models should inherit from it.
- **`get_current_user()`** (`apps.common.middlewares`): Thread-local middleware to get request user globally.
- **DRF permissions**: `IsAuthenticated` default. `BaseTestClass._test_permissions()` helper for testing role-based access.
- **SafeDeleteModel**: Soft deletes — `safedelete` library. `ShopProducts` uses this.
- **`BaseTestClass`** (`apps/common/baseclass_for_testing.py`): Test base with `APIClient`, `model_bakery`, `Faker`. Use `@pytest.mark.django_db` on test classes.
- **Fixtures**: JSON files in `apps/*/fixtures/`. Load with `load_data` command. Dump with: `python manage.py dumpdata business_app.brand --indent=4 --output=apps/business_app/fixtures/brands.json`

## Gotchas

- `STATIC_URL = "/static_output/"` (not `/static/`). Static root is `static_output/`.
- `.env` is gitignored. `REFERENCE.env` is the template — copy it and set `RUNNING_FROM=local` for local dev.
- `RUNNING_FROM` env var controls DB: `local` = SQLite, `remote` = PostgreSQL (reads `DB_REMOTE_*` vars).
- Redis caching is disabled in DEBUG mode (uses `DummyCache`). Production uses Redis on `127.0.0.1:6379`.
- `SessionTimeoutMiddleware` is active — sessions expire after `SESSION_EXPIRE_SECONDS` (default 600s).
- `drf-orjson-renderer` for API responses, not default DRF JSON.
- `drf-extensions` (`ExtendedSimpleRouter`) used in `business_app` URLs — supports nested routes.
- `ruff` is a dependency but has no config file — uses all defaults.

## CI / Deploy

GitHub Actions on push to `main`: SSH into Contabo server (`217.76.49.67`), `git pull`, `pip install`, `migrate`, `collectstatic`, restart gunicorn.

## Testing Conventions

- Tests live in `apps/<app>/tests/` or alongside modules as `test_*.py`
- `model_bakery` for test data generation, `Faker` for fake data
- `BaseTestClass.setUp()` creates a `SystemUser` with `baker.make` and loads fixtures if `self.fixtures` is defined
- `BaseTestClass.tearDown()` deletes all `GenericLog` entries
- Permission tests use `_test_permissions(url, allowed_roles, request_protocol)` — verifies allowed roles get non-403, disallowed roles get 403
- Group assignments in tests: `self.user.groups.add(Groups.SUPER_ADMIN.value)`