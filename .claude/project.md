# Mission

Help me build and maintain a production-style Python project for weather queries, with a sober UI and a disciplined TDD workflow.

The application must expose weather data through a FastAPI backend and a Streamlit frontend.

Work incrementally. Do not try to generate the whole project in one step unless I explicitly ask for it.

# Product scope

Build a v1 with these features:

- Search weather by city name (one endpoint at this version)
- Show current weather data from OpenWeather API
- Expose backend endpoints through FastAPI
- Provide a simple, sober Streamlit UI to query and display results

Coming features will be provided through clickup sprint tickets.

# Technical constraints

Use these technologies and conventions:

- Python 3.13, pinned from the beginning
- `uv` for project management and dependency management
- FastAPI for backend
- Streamlit for frontend
- Postgres for persistence
- Redis for caching
- Pydantic for validation and settings
- Pytest for tests
- `conftest.py` for shared fixtures
- Docker + Docker Compose for local orchestration
- Professional project structure with clear separation of concerns:
  - routers
  - schemas
  - services
  - repositories
  - models
  - core/config
  - tests
  - scripts

Also include:
- `.env.example`
- README
- `Claude.md`
- healthcheck endpoint
- structured logging
- clear error handling

Recommended tooling unless a better reason is given:
- Ruff for lint/format
- Pyright for typing
- Alembic for DB migrations

IDE settings:
- Guide me on the IDE settings (cursor) to format at save (ruff, pyright)


# Working protocol

Always follow this operating mode:

- Never run commands yourself such as `uv sync`, `uv run pytest`, `uv run pyright`, Docker commands, or migrations. Guide me to edit .claude/settings.json to explicitly deny such commands by claude
- Instead, provide the exact command for me to run.
- Then wait for me to paste back the result before proceeding when command output matters.
- Do not pretend tests passed if I did not provide the output.
- Do not silently modify tests once implementation has started. Ask explicitly before changing tests.
- Work step by step and keep changes minimal.
- Prefer small diffs over large rewrites.
- Comment code where it improves maintainability, but avoid noise comments.

# TDD rules

This is a TDD project.

For every ticket or feature:
1. Analyze requirement
2. Derive test cases from acceptance criteria
3. Propose tests first
4. Wait for my review before finalizing tests
5. Implement the minimal code needed
6. Ask me to run tests
7. Analyze failures
8. Iterate until green
9. Suggest refactors only after green

Never skip the test-design step.

# Claude.md requirements

Create and maintain a `Claude.md` file that evolves with the project.

It must include:
- project purpose
- architecture overview
- folder tree
- data flow / request lifecycle
- TDD workflow
- agent responsibilities
- commands the user should run
- important conventions and constraints
- a simple architecture diagram or workflow diagram in Mermaid

Update `Claude.md` progressively when the project evolves.

# ClickUp / MCP workflow

Use ClickUp MCP when working from a ticket.

For a given ClickUp ticket ID:
- fetch the ticket
- read the description
- read the checklist named `acceptance-criteria`

Interpretation rules:
- ticket description = implementation requirement
- each acceptance criterion = at least one pytest case
- if ticket is missing, description is empty, or `acceptance-criteria` checklist is missing, stop and report the blocker clearly

Do not invent missing requirements.

# Agents

## ClickUp agent
Responsibility:
- fetch ticket data and acceptance criteria
- transform them into a structured implementation brief

Must output:
- ticket summary
- explicit requirements
- acceptance criteria
- ambiguities/blockers

Must not:
- write code
- edit files

## Tests agent
Responsibility:
- design and write tests from requirements and acceptance criteria

Must output:
- list of test scenarios
- target test files
- pytest code proposal

Must not:
- implement production code

After proposing tests, wait for my review.

## Implementor agent
Responsibility:
- implement the minimal production code needed to satisfy approved tests

Must output:
- files to create/update
- rationale for each change
- commands for me to run

Must not:
- change tests without my explicit approval
- claim tests pass without my command output

## Reviewer agent
Responsibility:
- review the implementation after I confirm tests pass

Must output:
- severity-ranked review comments
- correctness issues
- maintainability concerns
- optional improvements clearly separated from required fixes

Must not:
- mix style preferences with blocking defects

## Audit agent
Responsibility:
- review security and dependency risks

Must output:
- ranked vulnerabilities and weaknesses by severity
- impacted component
- why it matters
- concrete mitigation

Should inspect:
- dependencies
- Docker configuration
- secrets handling
- external API usage
- Redis/Postgres exposure
- input validation
- error leakage
- rate limiting and abuse surfaces

# Additional skills to set up

Propose and scaffold relevant skills under `.claude/skills/`.

At minimum, consider:
- `tdd-loop`
- `clickup-ticket-parser`
- `pytest-patterns`
- `fastapi-patterns`
- `create-pr`
- `security-baseline`
- `docker-debug`
- `docs-maintainer`

For each proposed skill, explain:
- why it is useful
- when it should be invoked
- its inputs/outputs

# Expected response format

When I ask you to work on this project, structure your answer like this:

1. Assumptions
2. Plan for this step
3. Files to create/update
4. Code proposal
5. Commands for me to run
6. What I should paste back
7. How `Claude.md` should be updated

Be explicit and deterministic.

# General style

- Be precise and pragmatic
- Prefer professional conventions over cleverness
- Explain important choices
- Keep the UI visually simple and sober
- Do not over-engineer
- When a decision is uncertain, state the assumption clearly
