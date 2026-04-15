# Claude.md

Living document for Claude-assisted work on this project. Updated at the end of every phase.

## 1. Project purpose

_TBD — populated in Phase 1._
Short: weather queries by city name, served via FastAPI + Streamlit, persisted in Postgres, cached in Redis.

## 2. Architecture overview

_TBD — populated in Phase 2._

## 3. Folder tree

_TBD — populated in Phase 2._

## 4. Data flow / request lifecycle

_TBD — populated in Phase 3._

## 5. TDD workflow

See `.claude/project.md` for the authoritative rules. Summary:
1. Derive tests from acceptance criteria.
2. Propose tests; wait for review.
3. Implement minimal code.
4. User runs tests and pastes output.
5. Iterate to green; refactor after green.

## 6. Agent responsibilities

_TBD — populated in Phase 9._ See `.claude/project.md` for the spec of ClickUp / Tests / Implementor / Reviewer / Audit agents.

## 7. Commands the user should run

_TBD — populated as each phase lands._

## 8. Conventions and constraints

- Python 3.13 (pinned).
- `uv` for env and deps.
- Claude never runs `uv`, `docker`, `pytest`, migrations — proposes commands, user executes.
- Small diffs; no speculative code; no silent test edits.

## 9. Architecture diagram

_TBD — Mermaid diagram added in Phase 2.5._
