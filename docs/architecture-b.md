# Architecture B - Structured Context

This is the Strategy B architecture note for Module 5.5. It uses structured
repo context: `AGENTS.md`, `README.md`, and the main backend/frontend/test
files.

## What It Does

Task Tracker is a learning project from the AI-Assisted Coding course. It is a
FastAPI backend plus a single-file vanilla JavaScript Kanban frontend. The app
supports task creation, listing, filtering, retrieval, partial updates, deletes,
status-transition validation, due dates, overdue filtering, search, and combined
filters.

The project is intentionally local and lightweight: no authentication, no
database, no ORM, no frontend framework, and no external services.

## Main Components

- `app/main.py`: creates the FastAPI app, configures local CORS, registers
  `/health`, and defines all task CRUD routes.
- `app/models/__init__.py`: defines `TaskStatus`, `TaskPriority`, `TaskCreate`,
  `TaskUpdate`, and `TaskResponse` using Pydantic v2.
- `app/storage.py`: stores tasks in the process-local `_tasks` dictionary,
  generates UUID ids and UTC timestamps, applies filters, and computes overdue
  status.
- `app/business_rules.py`: holds the `VALID_TRANSITIONS` frozenset and rejects
  invalid status changes with 422.
- `frontend/index.html`: renders the board, filters, modal, drag/drop, and API
  calls in one self-contained HTML file.
- `frontend/BEHAVIOR_CONTRACT.md`: lists the manual browser checks expected
  before and after frontend changes.
- `tests/conftest.py`: resets in-memory storage around every test and provides
  the FastAPI `TestClient`.
- `tests/test_tasks.py`: covers CRUD, validation, transition rules, due dates,
  overdue behavior, search, and combined filters.

## Data Model

Tasks use exact enum values:

- Status: `ToDo`, `InProgress`, `Done`.
- Priority: `Low`, `Medium`, `High`.

Client input cannot include server-owned fields because the request models use
`extra="forbid"`. Titles are stripped, required, non-blank, and limited to 200
characters. Due dates use date-only `YYYY-MM-DD` semantics.

## Request Flow

1. The browser calls the API at `http://localhost:8000`.
2. `app/main.py` receives the route request.
3. FastAPI and Pydantic validate query params and body payloads.
4. For status updates, `validate_status_transition()` checks the current and
   requested status pair.
5. `app/storage.py` creates, reads, filters, updates, or deletes the task in the
   `_tasks` dictionary.
6. The API returns `TaskResponse` JSON or an error response.
7. The frontend updates the board, modal state, counts, and error messages.

## Deployment And Verification

The backend can run with uvicorn locally or inside the provided Docker image.
Docker uses `python:3.12-slim`, a non-root user, and a `/health` healthcheck.
The pytest suite is the primary automated verification layer and currently has
30 API tests.

## Verdict

Best for onboarding and repo-level understanding. It is broad enough to explain
the whole project and grounded enough to avoid architecture drift.

