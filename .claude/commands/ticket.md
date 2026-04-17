You are starting the TDD development workflow for a ClickUp ticket.

The ticket ID is provided as the argument to this command (e.g. `/ticket CU-86a...`).

Steps:
1. Use the ClickUp MCP tool `clickup_get_task` to fetch the task by ID.
2. Use `clickup_get_task_comments` if additional context is needed.
3. Invoke the `ticket-brief` skill to structure the raw ticket data into a dev brief.
4. Present the dev brief to the user and wait for confirmation before proceeding.
5. Once confirmed, spawn the `test-writer` agent with the dev brief as input.
6. Present the generated tests to the user for review.
7. Instruct the user to run `uv run pytest` — tests must FAIL at this point (no implementation yet).
8. Once the user validates tests implementationa dn confirms tests fail, spawn the `implementor` agent.
9. Instruct the user to run `uv run pytest` again — tests must PASS.
10. Remind the user to type `/commit` then `/pr` when ready.

Do not skip steps. Do not write implementation before tests are reviewed and confirmed failing.