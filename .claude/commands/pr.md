Create a GitHub pull request for the current branch against main.

Steps:
1. Run `git log main..HEAD --oneline` to list commits in this branch.
2. Run `git diff main..HEAD --stat` to summarize changed files.
3. If a ClickUp ticket ID and dev brief are available from this conversation, use them to populate the PR body. Otherwise derive context from the commits.

PR body format:
```
## Summary
<!-- 2-3 bullet points: what changed and why -->

## ClickUp ticket
<!-- Link: https://app.clickup.com/t/<id> — omit if no ticket -->

## Acceptance criteria
<!-- Paste the AC checklist as a GitHub task list:
- [ ] criterion 1
- [ ] criterion 2
-->

## Test plan
- [ ] All existing tests pass (`uv run pytest`)
- [ ] New tests cover every AC item
- [ ] Docker Compose stack starts cleanly

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

Show the proposed PR title and body. Then run `gh pr create` only after the user confirms.
