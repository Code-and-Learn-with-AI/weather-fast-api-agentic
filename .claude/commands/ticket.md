You are starting the TDD development workflow for a ClickUp ticket.

The ticket ID is provided as the argument to this command (e.g. `/ticket CU-86a...`).

Steps:
1. Use the ClickUp MCP tool `clickup_get_task` to fetch the task by ID.
2. Immediately use `clickup_update_task` to set the task status to "development".
3. Use `clickup_get_task_comments` if additional context is needed.
4. Invoke the `ticket-brief` skill to structure the raw ticket data into a dev brief.
5. Present the dev brief to the user and wait for confirmation before proceeding.
6. Once confirmed, derive a branch name from the ticket title: lowercase, hyphen-separated, prefixed with
   the ticket ID (e.g. `869cygabf-add-cache-source-label`). Instruct the user to run:
     git checkout main && git pull origin main && git checkout -b <branch-name>
   Wait for the user to confirm the branch is created before proceeding.
7. Invoke the `tdd-loop` skill to enforce TDD discipline for the rest of the session.
8. Spawn the `test-writer` agent with the dev brief as input.
9. Present the generated tests to the user for review.
10. Instruct the user to run `uv run pytest` — tests must FAIL at this point (no implementation yet).
11. Once the user confirms tests fail, spawn the `implementor` agent.
12. Instruct the user to run `uv run pytest` again — tests must PASS.
13. Remind the user to type `/commit` then `/pr` when ready.

Do not skip steps. Do not write implementation before tests are reviewed and confirmed failing.