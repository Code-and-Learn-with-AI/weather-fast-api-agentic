Look at the current git diff (staged and unstaged) and recent commit history.

Propose a single commit message following these rules:
- Format: `<type>(<scope>): <short summary>`
- Types: feat, fix, refactor, test, chore, docs
- Scope: the affected layer or module (e.g. router, cache, ui, docker, deps)
- Summary: imperative mood, under 72 characters, no period
- If a ClickUp ticket ID is known from this conversation, append it as a footer: `Refs: CU-<id>`

Show the proposed message in a code block. Do not commit — wait for the user to confirm.
