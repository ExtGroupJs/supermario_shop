# Constitution

## Core Rules

- ALWAYS use ENGLISH language for coding, including docstrings.
- Follow the DRF Structure Standard strictly.
- Prefer graph tools (codebase-memory-mcp) over grep/glob for structural discovery.
- Minimal changes: do not create new layers (services/repositories/selectors) unless a clear existing pattern justifies it.
- Tests first when feasible; use BaseTestClass and _test_permissions for role-based checks.
- One task at a time; run targeted tests before moving on.

## DRF Structure Standard

### Models
- One file per model under `<app>/models/<name>.py`, re-exported in `<app>/models/__init__.py`.
- Inherit `BaseModel` for `created_timestamp`/`updated_timestamp`. Use `models.Model` only for static/read-only entities.
- If audit-trail is needed, inherit `GenericLogMixin` FIRST (must be first), `SafeDeleteModel` second, `BaseModel` last:
  ```python
  class ShopProducts(GenericLogMixin, SafeDeleteModel, BaseModel):
      _safedelete_policy = SOFT_DELETE
  ```

### ViewSets
- One file per viewset under `<app>/views/<name>.py`. Filename matches model filename.
- Full CRUD → `class XViewSet(SerializerMapMixin, viewsets.ModelViewSet, GenericAPIView)`. When update not wanted, compose only needed mixins + `GenericViewSet`.
- Always declare all three filter backends:
  ```python
  filter_backends = [DjangoFilterBackend, filters.SearchFilter, CommonOrderingFilter]
  ```
- Default `CommonRolePermission` (or app-specific subclass). `@action(detail=False, methods=["GET"], permission_classes=[AllowAny])` for public endpoints.
- Override `perform_create` to attach actor: `serializer.save(seller=SystemUser.objects.get(id=self.request.user.id))` when applicable.
- Role-based row filtering goes in `get_queryset()` (mirror existing patterns).
- Pagination: `AllResultsSetPagination` when endpoint must return everything; `StandardResultsSetPagination` otherwise.

### Serializers
- One file per model under `<app>/serializers/<name>.py`. If multiple, keep in same file matching model name.
- Write serializer = flat `ModelSerializer` with FKs as bare PKs.
- Read serializer extends write, swapping FKs for nested read serializers. Add `__str__`, extra fields as needed.
- Wire via `SerializerMapMixin`: `{action}_serializer_class`.
- Annotate extra columns in viewset `queryset` with `.annotate(...)`; read serializer fields `read_only=True`.
- Parent+children: embed child serializer `many=True`; in view's `create()`, pop children and bulk-create.

### URLs
- Register each viewset in app's `urls.py`. `business_app` uses `ExtendedSimpleRouter`; others use `routers.DefaultRouter`.
- Mount in `project_site/urls.py` under prefixes.

## Graph Usage (Priority)
1. `search_graph` 2. `trace_path` 3. `get_code_snippet` 4. `check_index_coverage` 5. `query_graph` 6. `get_architecture`
- Check coverage for cited paths before negative/exhaustive claims.
- Fall back to grep/glob for literals, errors, config, non-code files, or insufficient graph results.

## Testing & Lint
- `pytest`, `ruff check .` (fix with `ruff check --fix .` if safe).
- Use `BaseTestClass`, `model_bakery`, `Faker`. Permission tests via `_test_permissions(url, allowed_roles, request_protocol)`.
- Group assignments: `self.user.groups.add(Groups.SUPER_ADMIN.value)` etc.