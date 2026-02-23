# Current Session State

## Just Completed
- F01 (Raindrop API Client): `RaindropClient` in `client.py`, reads `RAINDROP_TOKEN` env var, `fetch_tags()` calls API. 3 tests passing.
- F02 (Interactive CLI Menu): `run_menu()` loop in `main.py`, dispatches via `getattr(actions, handler_name)`. 3 tests passing.
- Created `actions.py` with `list_single_use_tags()` (covers F03/T01).

## In Progress
- F03 (List Single-Use Tags) — `actions.py` implementation already done; tests (T03) not yet written.

## Next Steps
1. Write `tests/test_actions.py` for `list_single_use_tags` (F03/T03)
2. Mark F03 tasks done, archive F03.md
3. Update features.md for F02 and F03 status
4. Run `/milestone` for remaining features

## Open Questions
- None.

## Feature Status

| Feature | Status | Tests |
|---------|--------|-------|
| F01 — Raindrop API Client | done | passing |
| F02 — Interactive CLI Menu | done | passing |
| F03 — List Single-Use Tags | in progress | not written |
