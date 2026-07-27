# CLAUDE.md - Task Tracker project memory

Guidance for an AI agent working in this repository. Read this before making
changes. The golden rules for this project: **read the diff before approving,
verify before moving on, and the human owns every acceptance.**

## What this project is
A small task tracker: a typed **FastAPI** backend with **in-memory storage
(no database)** and a single-file **vanilla-JavaScript Kanban frontend**. No
authentication. It is a learning project - keep it simple; do not add a
database, auth, an ORM, or a framework without being asked.

## Stack
- **Python 3.14** locally (the `.venv`); dependencies are pinned with lower
  bounds and target **3.11+**. If you build a Docker image, pick one explicit
  supported Python (e.g. `python:3.12-slim` or `3.13-slim`), not "latest".
- **FastAPI** + **Pydantic v2** (validation) + **Uvicorn** (server) + **python-dotenv**.
- Tests: **pytest** + Starlette `TestClient` (httpx).
- Frontend: plain HTML/CSS/JS in `frontend/index.html` (no build step, no framework).

## Commands
```bash
# setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# run backend (http://127.0.0.1:8000, docs at /docs)
uvicorn app.main:app --reload --port 8000

# serve frontend over HTTP (NOT file://), then open http://localhost:5500
python3 -m http.server 5500 --directory frontend

# tests
python -m pytest          # full suite (currently 30 passing)
python verify_a.py        # standalone data-model check (8 assertions)
```

## Architecture / key files
- `app/main.py` - FastAPI app instance, CORS middleware, and all routes.
- `app/models/__init__.py` - Pydantic models and enums (`TaskCreate`,
  `TaskUpdate`, `TaskResponse`, `TaskStatus`, `TaskPriority`). Input models use
  `extra="forbid"`.
- `app/storage.py` - in-memory dict store; filtering; `is_overdue()`.
- `app/business_rules.py` - status-transition validation (`VALID_TRANSITIONS`).
- `app/api/health.py` - `/health`. `app/core/config.py` - settings from `.env`.
- `frontend/index.html` - Kanban board, drag-and-drop, create/edit modal, filter bar.
- `tests/` - `test_tasks.py`, `test_health.py`, `conftest.py` (autouse storage reset).

## Business rules - DO NOT change these without asking
- **Status values are exactly** `ToDo`, `InProgress`, `Done`; **priority** is
  `Low`, `Medium`, `High`. The frontend and tests depend on these exact strings.
- **Valid status transitions:** `ToDo -> InProgress`, `InProgress -> Done`,
  `Done -> InProgress` (reopen). Everything else - including `ToDo -> Done`,
  `Done -> ToDo`, and same -> same - is rejected with **422**. Rules live in
  `VALID_TRANSITIONS` (a frozenset), validated on the `(current, new)` pair.
- **Overdue** is computed (never stored): a task is overdue if its `due_date`
  is before today **and** its status is not `Done`.
- `id` is a server-generated UUID string; `created_at`/`updated_at` are UTC and
  set in storage, never accepted from the client.
- Title is trimmed, must be non-empty, max 200 chars.

## HTTP contract
- `GET /tasks` filters (all optional, AND-combined): `status`, `priority`,
  `assignee`, `search` (title/description substring), `overdue`. No match -> 200
  with `[]`. Invalid `status`/`priority` -> 422.
- `POST /tasks` -> 201, `GET/PATCH /tasks/{id}` -> 200 (404 if missing),
  `DELETE /tasks/{id}` -> 204. Invalid body / bad transition -> 422.

## Frontend behavior (see frontend/BEHAVIOR_CONTRACT.md)
Three columns always render; cards sort High -> Medium -> Low; four UI states
(loading/ready/empty/error); drag is optimistic and reverts on a rejected move;
the modal blocks an empty title before any request and stays open on a 422.

## Verification habits
- Run `python -m pytest` after backend changes; keep it green (30 tests).
- After a refactor, re-run the behavior contract; a refactor must not change behavior.
- When adding a test, prove it with a **break test**: it must fail when the
  behavior it protects is broken, then pass when restored.
- Never weaken a test or add `try/except` just to make something pass.

## Out of scope (do not add unless explicitly asked)
Database/ORM, authentication or users, real-time updates, a mobile app, a JS
build system or framework, new external services.
