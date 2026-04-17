Transform raw ClickUp task data into a structured dev brief.

Given a ClickUp task (fetched via MCP), produce a brief with exactly these sections:

---
## Dev brief — <task title>

**Ticket:** CU-<id> | **Type:** feature | fix | chore (pick one)

### Context
<!-- 2-3 sentences: why this task exists, what problem it solves -->

### Requirements
<!-- Numbered list derived from the task description -->
1. ...

### Acceptance criteria
<!-- Exact AC checklist items from ClickUp, verbatim, each as a testable statement -->
- [ ] ...

### Out of scope
<!-- Anything explicitly excluded or that would be a separate ticket -->

### Affected layers
<!-- Which of: router, schema, service, repository, model, cache, ui, infra -->
---

Rules:
- Do not invent requirements not present in the ticket.
- AC items must be testable: each one must map to at least one unit or integration test.
- If the AC checklist is missing from the ticket, flag it explicitly and ask the user to add it before continuing.
- Keep the brief under one screen — no padding.
