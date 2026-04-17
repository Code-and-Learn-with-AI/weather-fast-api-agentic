Enforce the TDD discipline throughout the development session.

Rules (non-negotiable):
1. Tests must be proposed and reviewed BEFORE any implementation is written.
2. Tests must be confirmed FAILING by the user (`uv run pytest`) before implementation starts.
3. Implementation is written only to make the failing tests pass — no extra code.
4. Tests must be confirmed PASSING by the user before the cycle is marked complete.
5. If the user asks to skip a step, explain why it matters and ask again.

At each stage, clearly state which phase we are in:

  [TDD: TESTS PROPOSED — awaiting review]
  [TDD: TESTS APPROVED — awaiting failure confirmation]
  [TDD: TESTS FAILING — ready to implement]
  [TDD: IMPLEMENTATION PROPOSED — awaiting review]
  [TDD: TESTS PASSING — cycle complete]

Do not move to the next phase without explicit user confirmation.

When writing tests:
- Add relevant fixtures in conftest to produce reusable fixtures and simple test code.
- One test function per AC item minimum.
- Tests must be in the `tests/` directory following existing conventions.
- Use `pytest-asyncio` for async tests, `pytest-mock` for mocking, `fakeredis` for Redis.
- Follow patterns in `tests/conftest.py` for fixtures.

When writing implementation:
- Follow `fastapi-patterns` skill conventions.
- Minimal code — only what is needed to pass the tests.
- No speculative abstractions.