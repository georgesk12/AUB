# Documentation verification log

Part of Module 4.4. The lesson: AI-generated documentation describes what the
code is *claimed* to do, which is not always what it *actually* does. Every
docstring and README statement below was checked against the real code, and the
inaccuracies that surfaced were corrected. Documentation-only changes - no
behavior was altered, and `pytest` stayed green (30 passing) before and after.

## Method

For each source file I read the code first, wrote (or rewrote) the docstring
from what the code does, then re-read the README's claims against `app/main.py`,
`app/storage.py` and the `Dockerfile`. A claim only counts as verified once the
code path that backs it was traced.

## Inaccuracies caught and fixed

### 1. FastAPI `description` was stale and user-visible

- **Claimed:** `app/main.py` created the app with
  `description="Learning-project task tracker (Module 2)."` This string is
  rendered live at `/docs`, so anyone opening the interactive docs saw a
  Module-2 label on a Module-4 app.
- **Reality:** the API now has five task routes with filtering and
  status-transition rules plus health/landing endpoints - nothing about it is
  Module-2-specific.
- **Fix:** rewrote the description to actually list what the API does: "A small
  task tracker REST API: create, list/filter, read, update (with
  status-transition rules) and delete tasks. In-memory storage, no
  authentication."

### 2. `app/api/health.py` module docstring was a Module 1 relic

- **Claimed:** "This is the one working endpoint the skeleton ships with ... the
  foundation is sound and **Module 2** can build on it."
- **Reality:** it is no longer the only endpoint (there are seven routes), and
  "Module 2 can build on it" has been false for three modules. It is now also
  the target of the Docker `HEALTHCHECK`, which the docstring never mentioned.
- **Fix:** rewrote it to describe the endpoint as a liveness probe, note the
  exact 200 payload, and mention its use by the Docker health check.

### 3. `app/storage.py` claimed persistence "in a later module"

- **Claimed:** "No database and no ORM - swapped for real persistence in a later
  module."
- **Reality:** there is no such later module in this course, and CLAUDE.md
  explicitly lists a database/ORM as **out of scope**. The claim promised a
  future that does not exist.
- **Fix:** rewrote the module docstring to state plainly that the in-memory dict
  is the whole store, process-local, and cleared on restart by design - with no
  promise of future persistence.

### 4. `app/main.py` module docstring referenced "Module 2.2"

- **Claimed:** the module docstring opened by tagging the file to a specific
  early-module part.
- **Reality:** the file is the app's current entry point spanning all modules.
- **Fix:** rewrote it to describe the app (FastAPI instance, CORS for the local
  frontend, in-memory storage, no auth) without a module tag.

## Claims checked and confirmed accurate (no change needed)

- **README endpoints table** vs `app/main.py`: every row matches - `POST /tasks`
  -> 201, `GET /tasks` -> 200, `GET/PATCH /tasks/{id}` -> 200 with 404 when
  missing, `PATCH` -> 422 on an invalid transition, `DELETE` -> 204, plus
  `GET /health` and `GET /`.
- **README "30 tests"** vs the suite: `pytest` reports 30 passing.
- **README Docker section** vs the `Dockerfile`: base image `python:3.12-slim`,
  non-root user, `/health`-based `HEALTHCHECK`, and `app/`-only copy all match
  the actual Dockerfile and `.dockerignore`.
- **`is_overdue` docstring** vs code: "due date strictly before today AND not
  Done" matches `task.due_date < today and task.status != TaskStatus.DONE`.
- **Status-transition docstring** vs `VALID_TRANSITIONS`: the three allowed
  pairs and the same->same rejection match the frozenset exactly.

## Outcome

Four inaccurate claims corrected, six spot-checked and confirmed. All changes
were to comments and docstrings (and one user-visible `description` string); no
executable logic changed, and the test suite is still green at 30 passing.
