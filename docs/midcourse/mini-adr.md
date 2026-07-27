# Mini-ADR - Mid-Course Feature Sprint

**Status:** Accepted · **Scope:** two small, end-to-end features on the existing
in-memory Task Tracker (no database, no auth).

## Context
The Task Tracker already has a strict Pydantic data model, five CRUD endpoints,
status-transition rules, a Kanban frontend, and a pytest suite. The sprint adds
two features without breaking the existing behavior contract.

## Decision 1 - Due dates
Add an optional `due_date: Optional[date] = None` to `TaskCreate`, `TaskUpdate`
and `TaskResponse`. Using Pydantic v2's `date` type means an invalid string is
rejected with 422 automatically, and JSON serialization to `YYYY-MM-DD` is free.
Day granularity (`date`, not `datetime`) matches a date picker and keeps the
model simple.

## Decision 2 - Overdue is computed, not stored
`is_overdue(task, today)` lives in `storage.py` and returns True only when the
task has a due date **before today** and its status is **not Done**. Overdue is
computed on read (for the `?overdue=` filter) and recomputed with the same rule
in the frontend for the card pill.

**Rejected alternative:** storing an `overdue` boolean on the task. It would go
stale the moment the date advances or the status changes, and would need a
recompute on every write. A computed value is always correct.

## Decision 3 - Search + combined filters in the backend
Extend `GET /tasks` and `storage.get_all_tasks` with `search` (case-insensitive
substring of title or description), `assignee` (case-insensitive exact), and
`overdue`, combined with the existing `status`/`priority` using AND. The
frontend builds the query string and re-fetches.

**Rejected alternative:** filtering on the frontend in JavaScript. It is not
testable through the API and the brief explicitly asks for `GET /tasks`
filtering. Doing it server-side keeps one source of truth and lets pytest cover
it.

## Other alternatives the AI suggested and I rejected as out of scope
- Full-text / fuzzy search or a search index - overkill; a substring match is enough for this scale.
- A separate `/overdue` endpoint - unnecessary; a query param on `/tasks` composes with the other filters.
- Saved filter presets / persistence - explicitly listed as an optional extension that adds settings design not central to this sprint.

## Consequences
- No model migration or storage engine change; everything stays in memory.
- The existing behavior contract and all prior tests keep passing.
- Overdue and filtering are fully covered by new pytest tests and proven with break tests.
