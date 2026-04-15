# Weather FastAPI Agentic — Incremental Build Plan

## Context

The project directory contains only `.claude/project.md` — a detailed spec for a production-style weather app (FastAPI backend + Streamlit frontend, Postgres, Redis, Docker, TDD). Nothing else exists yet: no `pyproject.toml`, no source tree, no Docker files, no skills.

The spec mandates strict TDD, small diffs, and explicit user-run commands. The user reinforced: **"one tiny, simple thing at a time"** — so this plan is a roadmap of micro-steps, each reviewable and reversible. We will execute one step at a time, loop-style (propose → review → adjust → validate → next).

**Note on file location:** Plan-mode constrains me to edit only this file. The user asked for the plan under `.claude/plan/` in the project. On `ExitPlanMode` approval, we will copy this file to `/home/amassoudi/PersonalProjects/weather-fast-api-agentic/.claude/plan/build-roadmap.md` as the first executed action.

---

## Guiding principles (from `project.md`)

- TDD: tests proposed → reviewed → implementation → run → iterate.
- User runs all commands; Claude never executes `uv`, `docker`, `pytest`, migrations.
- Minimal diffs; no speculative code.
- `Claude.md` evolves with the project.
- Each ClickUp ticket drives a feature via `acceptance-criteria` checklist.

---

## Phase 0 — Alignment & prerequisites (no code)

**0.1** Confirm open questions (see *Open questions* section below) via AskUserQuestion before any file is written.
**0.2** Agree on the step granularity of this plan.

## Phase 1 — Repo bootstrap (skeleton only, no app logic)

Each step = one small PR-sized change.

**1.1** Create `.gitignore`, `.python-version` (3.13), `README.md` (stub), `Claude.md` (stub with the 8 required sections, mostly TBD).
**1.2** Initialize `pyproject.toml` via `uv init` — pin Python 3.13, add project metadata. User runs `uv init` + `uv python pin 3.13`.
**1.3** Add `.env.example` with placeholder keys (`OPENWEATHER_API_KEY`, `DATABASE_URL`, `REDIS_URL`, `LOG_LEVEL`).
**1.4** Add dev tooling: Ruff, Pyright, Pytest, pytest-asyncio, httpx. User runs `uv add --dev ...`.
**1.5** Configure Ruff + Pyright in `pyproject.toml`; add `pytest` config and `conftest.py` placeholder.
**1.6** Guide for Cursor IDE: format-on-save with Ruff, Pyright diagnostics.

**Gate:** `uv run ruff check .` and `uv run pyright` both pass on empty tree.

## Phase 2 — Project structure (empty modules + a first failing test)

**2.1** Create directory tree: `app/{routers,schemas,services,repositories,models,core}`, `tests/`, `scripts/`, `app/__init__.py` everywhere. All empty.
**2.2** Add `app/core/config.py` — Pydantic `Settings` (BaseSettings), env-driven. Tests first: loads from env, defaults, required-field errors.
**2.3** Add `app/main.py` — minimal FastAPI app. Tests first: app instantiation, OpenAPI served.
**2.4** Add `/health` endpoint. Tests first: returns `200 {"status": "ok"}`.
**2.5** Structured logging bootstrap (`app/core/logging.py`): JSON logs, request-id middleware. Tests for formatter output.

**Gate:** `uv run pytest` green; `uv run uvicorn app.main:app` serves `/health`.

## Phase 3 — Weather feature v1 (TDD, one slice at a time)

Driven by ClickUp ticket(s). Until a ticket exists, we work from the spec's "v1 features".

**3.1** Schemas: `WeatherResponse` (Pydantic). Tests: serialization, field constraints.
**3.2** OpenWeather client (`app/services/openweather.py`): async httpx call, timeout, error mapping. Tests use `httpx.MockTransport` — no real network.
**3.3** Service layer (`app/services/weather_service.py`): orchestrates client + (later) cache + repo. Tests with mocked client.
**3.4** Router (`app/routers/weather.py`): `GET /weather?city=...`. Tests via `httpx.AsyncClient` against the app.
**3.5** Error handling: 404 city-not-found, 502 upstream-failure, 422 validation. Tests for each branch.

**Gate:** end-to-end request works with a real API key (user confirms manually).

## Phase 4 — Persistence (Postgres + Alembic)

**4.1** Add `sqlalchemy`, `asyncpg`, `alembic` dev deps.
**4.2** `app/models/weather_query.py` — ORM model logging past queries (city, timestamp, payload).
**4.3** Alembic init + first migration. User runs `uv run alembic ...`.
**4.4** Repository layer (`app/repositories/weather_repo.py`) with integration tests against a test Postgres (via Docker Compose).
**4.5** Wire service → repo (persist each successful query).

## Phase 5 — Caching (Redis)

**5.1** Add `redis` async client dep.
**5.2** Cache layer (`app/services/cache.py`) with TTL. Tests with fakeredis.
**5.3** Wire service: cache-aside around OpenWeather client. Tests assert client not called on cache hit.

## Phase 6 — Docker Compose

**6.1** `Dockerfile` for API (multi-stage, non-root user). Tests: image builds.
**6.2** `docker-compose.yml` — api, postgres, redis, streamlit. `.env` wiring.
**6.3** Healthchecks for each service.

## Phase 7 — Streamlit UI

**7.1** `ui/app.py` — single page: city input, submit, render response. Sober styling.
**7.2** Call FastAPI via env-configured base URL. Handle error states visibly but plainly.

## Phase 8 — Skills scaffolding (`.claude/skills/`)

Propose incrementally; don't create all at once. Priority order:
1. `tdd-loop` — enforces propose-tests → review → implement → run.
2. `clickup-ticket-parser` — fetches ticket + `acceptance-criteria`, emits brief.
3. `pytest-patterns` — fixtures, async testing, MockTransport recipes.
4. `fastapi-patterns` — router/schema/service/repo conventions.
5. `docs-maintainer` — keeps `Claude.md` current.
6. `security-baseline` — checklist used by Audit agent.
7. `docker-debug` — common compose/healthcheck issues.
8. `create-pr` — PR body template tied to ticket IDs.

For each skill we will define: purpose, trigger, inputs, outputs, before scaffolding.

## Phase 9 — Agents

Spec already defines four: ClickUp, Tests, Implementor, Reviewer, Audit. We will add each as a subagent config under `.claude/agents/` when first used — not upfront.

---

## Decisions (locked in Phase 0)

- **OpenWeather API key**: available — live integration allowed from Phase 3.
- **ClickUp MCP**: not configured yet — we proceed from the spec's v1 scope; revisit when MCP is wired.
- **Start point**: step 1.1 — stubs for `.gitignore`, `README.md`, `Claude.md`.
- **Plan location**: on approval, copy this file to `<project>/.claude/plan/build-roadmap.md` as the first executed action.
- **Git**: to be confirmed at step 1.1 (local `git init` vs. existing remote).

---

## Verification strategy

- Every phase ends with a **Gate**: a concrete command the user runs that must pass.
- No step is "done" until the user pastes back the command output.
- `Claude.md` is updated at the end of each phase (folder tree, data flow, commands).
- Mermaid architecture diagram added in Phase 2.5 and revised at each persistence/cache/UI addition.

---

## Loop protocol for us

1. I propose the next micro-step (files, diff sketch, tests first).
2. You review / suggest / reject.
3. I adjust until you say "go".
4. You run the commands, paste output.
5. We move to the next step.

No step larger than ~1 file + its tests unless you explicitly approve a bigger chunk.
