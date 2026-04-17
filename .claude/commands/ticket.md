You are starting the TDD development workflow for a ClickUp ticket.

The ticket ID is provided as the argument to this command (e.g. `/ticket CU-86a...`).

Steps:
1. Use the ClickUp MCP tool `clickup_get_task` to fetch the task by ID.
2. Use `clickup_get_task_comments` if additional context is needed.
3. Invoke the `ticket-brief` skill to structure the raw ticket data into a dev brief.
4. Present the dev brief to the user and wait for confirmation before proceeding.
5. Once confirmed, derive a branch name from the ticket title: lowercase, hyphen-separated, prefixed with
   the ticket ID (e.g. `869cygabf-add-cache-source-label`). Instruct the user to run:
     git checkout main && git pull origin main && git checkout -b <branch-name>
   Wait for the user to confirm the branch is created before proceeding.
6. Spawn the `test-writer` agent with the dev brief as input.
7. Present the generated tests to the user for review.
8. Instruct the user to run `uv run pytest` — tests must FAIL at this point (no implementation yet).
9. Once the user confirms tests fail, spawn the `implementor` agent.
10. Instruct the user to run `uv run pytest` again — tests must PASS.
11. Remind the user to type `/commit` then `/pr` when ready.

Do not skip steps. Do not write implementation before tests are reviewed and confirmed failing.