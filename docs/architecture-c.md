# Architecture C - Targeted Context

This is the Strategy C architecture note for Module 5.5. It uses a deliberately
limited file set: `app/main.py`, `app/models/__init__.py`, `app/storage.py`,
`app/business_rules.py`, `tests/test_tasks.py`, and
`frontend/BEHAVIOR_CONTRACT.md`.

## What It Does

The backend is a FastAPI task API backed by in-memory storage. It supports task
CRUD, AND-combined task filters, due-date/overdue behavior, and strict
status-transition validation. The frontend contract describes a Kanban board
that depends on those API rules for drag/drop and modal edits.

## Backend Shape

`app/main.py` owns the route layer:

- `POST /tasks` returns 201.
- `GET /tasks` returns 200 with filtered results or `[]`.
- `GET /tasks/{task_id}` returns 200 or 404.
- `PATCH /tasks/{task_id}` returns 200, 404, or 422 for invalid status moves.
- `DELETE /tasks/{task_id}` returns 204 or 404.

`app/models/__init__.py` owns request/response validation. `TaskCreate` and
`TaskUpdate` reject unknown fields. `TaskResponse` includes generated server
fields.

`app/storage.py` owns ids, timestamps, filters, overdue computation, and the
module-level `_tasks` dictionary.

`app/business_rules.py` owns the transition allow-list:

- `ToDo -> InProgress`
- `InProgress -> Done`
- `Done -> InProgress`

Everything else, including same-status moves, is rejected.

## Frontend Contract

The board must preserve three columns, column counts, priority sorting, loading,
empty, and error states. Drag/drop sends PATCH only for a new target column and
must revert on 422. The create/edit modal must block blank titles locally,
refresh after valid saves, and keep the modal open on invalid transitions.

## Test Contract

The API tests verify CRUD status codes, validation failures, transition matrix
rules, due dates, overdue filtering, search behavior, combined filters, and
invalid filter values. Tests use a storage reset fixture so each test starts
from an empty in-memory task store.

## Limits Of This Pass

This pass did not inspect Docker, CI, README, security docs, or all frontend
implementation details. Its claims are intentionally narrower and more precise.

## Verdict

Best for correctness-sensitive work on API behavior because it avoids unrelated
context and names what was not inspected.

