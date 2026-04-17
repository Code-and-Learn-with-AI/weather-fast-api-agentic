Project conventions for FastAPI code in this codebase. Apply these whenever adding or modifying an endpoint, service, or repository.

### Layering
```
router → service → repository → model
       ↘ cache (optional, cache-aside)
```
- Routers only handle HTTP: parse input, call service, map exceptions to HTTPException.
- Services contain business logic. They are injected with dependencies (repo, cache, http client).
- Repositories handle DB access only. They accept an `AsyncSession` and return ORM models or domain objects.
- Schemas (Pydantic) are the contract between layers — never pass ORM models to the router.

### Dependency injection
- All dependencies use `Depends()` in router function signatures.
- Settings are injected via `get_settings()` (not imported directly).
- DB session via `get_db_session()` from `app.core.database`.
- Redis via `get_redis()` from `app.routers.weather` (or extracted to `app.core.redis` if reused).
- Use `TYPE_CHECKING` guards for cross-layer imports to avoid circular imports.

### Error handling
- `CityNotFoundError` → 404
- `WeatherServiceError` → 502
- Never catch broad `Exception` in routers — let FastAPI handle 422 validation errors.

### Schemas
- Use `Pydantic v2` (`model_validate`, `model_dump_json`, `model_validate_json`).
- All response models have explicit field types — no `Any`.

### Testing conventions
- Router tests: use `async_client` fixture with `app.dependency_overrides` to mock DB and Redis.
- Service tests: mock `httpx.AsyncClient` with `MockTransport` or `pytest-mock`.
- Repo tests: use `db_session` fixture (real Postgres, transaction rollback).
- Cache tests: use `fake_redis` fixture (`fakeredis`).

### Style
- `from __future__ import annotations` at top of every file with forward references.
- No inline comments unless the WHY is non-obvious.
- Line length: 120 (ruff enforced).
