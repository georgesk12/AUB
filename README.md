# Task Tracker

A small, typed task tracker with a FastAPI backend and a vanilla-JavaScript
Kanban frontend. Built across Modules 1-3 of the AI-Assisted Coding course and
extended in the mid-course sprint: every file was AI-drafted, then reviewed,
run, tested and verified by hand.

Stack: Python + FastAPI + Pydantic v2, in-memory storage (no database), no
authentication. Frontend is a single self-contained HTML file. See
`docs/midcourse/mini-adr.md` for the design decisions.

## Final Project

Branch reviewed: `final-project`

### What this submission demonstrates

- The existing Task Tracker still runs and stays inside the intended course
  scope - no new product features were added.
- CI runs the pytest suite on push and/or pull request.
- The Docker image builds and runs, with `/health` returning 200 and the process
  running as a non-root user.
- AI review, security, and ownership evidence live in `docs/`.

### How to run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend at <http://127.0.0.1:8000> (docs at `/docs`, health at `/health`). Serve
the frontend in a second terminal with
`python3 -m http.server 5500 --directory frontend`, then open
<http://localhost:5500>.

### How to run tests

```bash
python -m pytest
```

### How to run with Docker

```bash
docker build -t task-tracker .
docker run --rm -p 8000:8000 task-tracker
curl http://127.0.0.1:8000/health
```

### Evidence files

- `docs/release-evidence.md` - baseline, CI, Docker, and claim-vs-reality checks.
- `docs/final-ai-review.md` - AI code review, security review, and ownership.
- `docs/ai-playbook.md` - personal AI playbook and decision card.

### AI assistance summary

AI helped draft or review: CI, Docker, docs, security, and debugging. I verified
the work by: running the tests, reviewing every diff, checking Docker `/health`,
and doing a manual security scan. One AI suggestion I rejected: the Docker
`--workers 4` recommendation, which would have broken the per-process in-memory
store.

## Features

- Strict data model with Pydantic v2 validation (`extra="forbid"`, title
  stripping, enum-checked status and priority).
- Five CRUD endpoints plus status-transition business rules (a task cannot skip
  stages or move backward out of Done).
- **Due dates** with an **overdue** rule (past due and not Done), including an
  `?overdue` filter and an overdue pill on cards.
- **Search + combined filters**: text search over title/description combined
  with status, priority, assignee and overdue.
- Kanban frontend: three columns, priority sorting, drag-and-drop with
  optimistic move and revert on rejection, a create/edit modal, and a
  search/filter bar.
- A pytest suite (**30 tests**) covering happy paths, failure cases, the
  transition matrix, and the new features - proven with deliberate break tests.

## Endpoints

| Method | Path          | Success | Notes                                                        |
|--------|---------------|---------|--------------------------------------------------------------|
| GET    | `/health`     | 200     | Health check                                                 |
| GET    | `/`           | 200     | Landing payload / links                                      |
| POST   | `/tasks`      | 201     | Create a task (422 on invalid input, incl. bad `due_date`)   |
| GET    | `/tasks`      | 200     | List/filter (see query params below)                         |
| GET    | `/tasks/{id}` | 200     | 404 if not found                                             |
| PATCH  | `/tasks/{id}` | 200     | 404 if not found, 422 on invalid transition                  |
| DELETE | `/tasks/{id}` | 204     | Empty body; 404 if not found                                 |

`GET /tasks` query params (all optional, combined with AND):
`status`, `priority`, `assignee`, `search` (substring of title or description),
`overdue` (`true`/`false`). Invalid `status`/`priority` values return 422; no
matches returns 200 with `[]`. Interactive docs at `/docs`.

## Run the backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend runs at <http://127.0.0.1:8000> (docs at `/docs`).

## Open the frontend

The frontend must be served over HTTP (not opened as a `file://` path) so its
API calls work. With the backend running, in a second terminal:

```bash
python3 -m http.server 5500 --directory frontend
```

Then open <http://localhost:5500>. (VS Code Live Server on `frontend/index.html`
works too.) CORS is already configured for local origins.

## Run with Docker

A multi-stage `Dockerfile` builds a slim image (`python:3.12-slim`) that runs
the backend as a **non-root** user. Build and run it:

```bash
docker build -t task-tracker .
docker run --rm -p 8000:8000 task-tracker
```

The API is then at <http://127.0.0.1:8000> (docs at `/docs`), same as the
`uvicorn` command above but with no `--reload`. The image ships a
`HEALTHCHECK` that polls `/health`, so `docker ps` shows the container as
`healthy` once it is up. Only `app/` is copied into the image; tests, docs, the
frontend and `.env` are excluded via `.dockerignore`.

## Run the tests

```bash
python -m pytest          # full suite (30 tests)
python verify_a.py        # standalone data-model check (8 assertions)
```

## Design note

The reasoning behind the main decisions - storage model, status rules, CI and
Docker design, and the tradeoffs and open questions behind them - is written up
in [`docs/technical-note.md`](docs/technical-note.md). Read it to understand
*why* the project is built the way it is, not just *what* it does.

## Mid-course documentation

`docs/midcourse/` contains the sprint deliverables: `user-stories.md`,
`mini-adr.md`, `prompt-log.md`, `verification.md`, and `reflection.md`. The
frontend behavior contract is at `frontend/BEHAVIOR_CONTRACT.md`, the Module 3
debugging log is at `DEBUGGING_LOG.md`, the documentation-verification log is at
`docs/documentation-verification.md`, and the Module 4.5 AI code-review triage is
at `docs/code-review-4.5.md`.

## AI-assisted-coding artifacts (Module 5)

The course closing set - review, governance and planning docs, no app code:
my [**personal AI playbook**](docs/ai-playbook.md) (which tool I reach for when,
and the rules I will not break), the [security review](docs/security-review.md),
the [governance retrospective](docs/governance-worksheet.md) and
[AI-usage rules](docs/ai-usage.md), the
[comments feature plan](docs/decision/comments-feature-plan.md), and the
[architecture note](docs/architecture.md) with its context-strategy comparison.
Agent guidance for the repo lives in `AGENTS.md` and `CLAUDE.md`.

## Project structure

```
task-tracker-api/
├── app/
│   ├── main.py            # FastAPI app + all routes (incl. filters)
│   ├── models/            # Pydantic models (enums, Create/Update/Response, due_date)
│   ├── storage.py         # in-memory storage + filtering + is_overdue
│   ├── business_rules.py  # status-transition validation
│   ├── core/config.py     # settings loaded from .env
│   └── api/health.py      # /health endpoint
├── frontend/
│   ├── index.html         # Kanban board, modal, filters (self-contained)
│   └── BEHAVIOR_CONTRACT.md
├── tests/
│   ├── conftest.py        # fixtures (storage reset, client, created_task)
│   ├── test_tasks.py      # API tests
│   └── test_health.py
├── docs/midcourse/        # mid-course project documentation
├── verify_a.py            # data-model verification script
├── DEBUGGING_LOG.md
├── requirements.txt
├── .env.example
└── .gitignore
```
