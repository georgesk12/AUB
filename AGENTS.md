# AGENTS.md - Task Tracker Codex guidance

This file is the repo-level guidance for Codex App threads. Module 5 is about
review, governance, planning, and documentation. Default to read-first and
docs-first work unless the user explicitly approves a code change.

## Project Summary

Task Tracker is a learning project from the AI-Assisted Coding course:

- FastAPI backend with Pydantic v2 models.
- Process-local in-memory storage, no database and no ORM.
- Vanilla JavaScript Kanban frontend in one self-contained HTML file.
- Pytest suite for the API.
- GitHub Actions CI and a Dockerfile for the backend.

Do not add authentication, users, a database, an ORM, a frontend framework, or a
new external service unless the user explicitly asks.

## Key Files

- `app/main.py` - FastAPI app, CORS middleware, task routes.
- `app/models/__init__.py` - enums and Pydantic request/response models.
- `app/storage.py` - in-memory task store, filters, overdue computation.
- `app/business_rules.py` - status-transition allow-list.
- `app/api/health.py` - `/health` endpoint used by Docker healthcheck.
- `frontend/index.html` - Kanban UI, modal, filters, drag/drop.
- `tests/` - pytest suite and fixtures.
- `.github/workflows/ci.yml` - CI test workflow.
- `Dockerfile` and `.dockerignore` - backend container build.
- `docs/` - Module 4/5 documentation artifacts.

## Commands

Run commands from the repo root.

```bash
# install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# backend
uvicorn app.main:app --reload --port 8000

# frontend
python3 -m http.server 5500 --directory frontend

# tests
python -m pytest
python verify_a.py

# docker
docker build -t task-tracker .
docker run --rm -p 8000:8000 task-tracker
```

The full pytest suite is expected to pass before and after meaningful backend
or contract changes.

## Business Rules

Preserve these unless the user explicitly asks to change them:

- Status values are exactly `ToDo`, `InProgress`, `Done`.
- Priority values are exactly `Low`, `Medium`, `High`.
- Allowed transitions are:
  - `ToDo -> InProgress`
  - `InProgress -> Done`
  - `Done -> InProgress`
- Rejected transitions include `ToDo -> Done`, `Done -> ToDo`, and same-status
  moves. Invalid transitions return 422.
- Task IDs and timestamps are generated server-side.
- Client input must not accept `id`, `created_at`, or `updated_at`.
- Titles are trimmed, required, non-blank, and at most 200 characters.
- `due_date` is optional and uses date-only `YYYY-MM-DD` semantics.
- A task is overdue only when `due_date` is before today and status is not
  `Done`.
- `GET /tasks` filters combine with AND: `status`, `priority`, `assignee`,
  `search`, and `overdue`.

## Module 5 Guardrails

For Module 5 tasks:

- Prefer read-only analysis first.
- Put deliverables in `docs/` unless the user explicitly asks otherwise.
- Do not modify `app/`, `frontend/`, tests, CI, Docker, or dependencies during
  review/governance/planning tasks without explicit approval.
- If asked for a security review, feature plan, architecture comparison, or
  playbook, produce a document or recommendation, not application code.
- Cite files and line numbers for repo claims whenever possible.
- Say when a claim is an inference or when a file was not inspected.
- Start a fresh bounded thread/task for separate Module 5 activities when the
  user asks.

## Security And Governance Notes

- Do not expose secrets, tokens, credentials, private data, or `.env` contents.
- Treat `.env` as local configuration, not source material to quote.
- Do not run destructive commands such as `rm`, `git reset`, or broad cleanup
  commands unless the user explicitly requests and approves them.
- Security-review output must distinguish:
  - valid findings,
  - false positives,
  - generic noise,
  - course-scope decisions that would matter in production.
- The absence of authentication is intentional for this learning project, but
  should still be named as a production risk when relevant.

## Review Expectations

- Read the relevant files before proposing conclusions.
- Do not invent folders, frameworks, routes, or test names.
- Keep changes small and easy to inspect.
- Do not weaken tests to make the suite pass.
- After any approved behavior change, run targeted checks and the full pytest
  suite when practical.
- For frontend behavior claims, use the behavior contract in
  `frontend/BEHAVIOR_CONTRACT.md` as the checklist.

