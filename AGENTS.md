# AGENTS.md

## Project

Django 5.1.1 + DRF 3.15.2 auto parts shop (Geely vehicles). Python 3.11. Session-based auth. Spanish locale (`es-es`). `USE_TZ = False`, timezone `America/Havana`.

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