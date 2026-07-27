# Task Tracker API

A small, typed REST API for tracking tasks on a Kanban-style board (ToDo /
InProgress / Done). Built as a learning project for the AI-Assisted Coding
course: every file was AI-drafted, then reviewed, run, tested and verified by
hand. Modules 1 and 2 are complete - data model, CRUD endpoints, status
transition rules, and a pytest suite proven with a deliberate break test.

Stack: Python + FastAPI + Pydantic v2, in-memory storage (no database), no
authentication. See the ADR for the reasoning behind these choices.

## Features

- Strict data model with Pydantic v2 validation (`extra="forbid"`, title
  stripping, enum-checked status and priority).
- Five CRUD endpoints for tasks.
- Status-transition business rules (a task cannot skip stages or move
  backward out of Done).
- A pytest suite (17 tests) covering happy paths, failure cases and the
  transition matrix.

## Endpoints

| Method | Path              | Success | Notes                                        |
|--------|-------------------|---------|----------------------------------------------|
| GET    | `/health`         | 200     | Health check                                 |
| GET    | `/`               | 200     | Landing payload / links                      |
| POST   | `/tasks`          | 201     | Create a task (422 on invalid input)         |
| GET    | `/tasks`          | 200     | List tasks; optional `status` / `priority`   |
| GET    | `/tasks/{id}`     | 200     | 404 if not found                             |
| PATCH  | `/tasks/{id}`     | 200     | 404 if not found, 422 on invalid transition  |
| DELETE | `/tasks/{id}`     | 204     | Empty body; 404 if not found                 |

Interactive docs are served at `/docs` (Swagger UI) when the server runs.

## Status transition rules

Allowed: `ToDo -> InProgress`, `InProgress -> Done`, `Done -> InProgress`
(reopen). Rejected with 422: `ToDo -> Done` (skips a stage), `Done -> ToDo`
(revert), and any same-to-same change.

## Setup and run (macOS / Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Then open <http://127.0.0.1:8000/docs>.

## Tests

```bash
python -m pytest          # runs the full suite
python verify_a.py        # standalone data-model check (8 assertions)
```

## Project structure

```
task-tracker-api/
├── app/
│   ├── main.py            # FastAPI app + all routes
│   ├── models/            # Pydantic models (enums, TaskCreate/Update/Response)
│   ├── storage.py         # in-memory storage layer
│   ├── business_rules.py  # status-transition validation
│   ├── core/config.py     # settings loaded from .env
│   └── api/health.py      # /health endpoint
├── tests/
│   ├── conftest.py        # fixtures (storage reset, client, created_task)
│   ├── test_tasks.py      # 17 API tests
│   └── test_health.py
├── verify_a.py            # data-model verification script
├── requirements.txt
├── .env.example
└── .gitignore
```
