# Release Evidence

Factual release-check evidence for the final project. Captured on the
`final-project` branch. Text logs only.

## Baseline

- **Branch:** `final-project` (created from `main`).
- **Date:** 2026-07-29.
- **Local app run command:** `uvicorn app.main:app --port 8000`
  (with `.venv` active: `source .venv/bin/activate`).
- **/health result:** `GET /health` returned HTTP 200 with
  `{"status":"ok","timestamp":"2026-07-29T19:15:45.968858+00:00"}`.
- **Frontend check:** served with `python3 -m http.server 5500 --directory frontend`
  and opened at `http://localhost:5500`. The Kanban board renders its three
  columns and the create/edit modal opens, validates an empty title, and saves -
  verified in Module 3 with browser checks (optimistic drag with revert on a
  rejected move, modal stays open on a 422).
- **Test command:** `python -m pytest`
- **Test result:** `30 passed, 4 warnings in 0.07s` (Python 3.14). The warnings
  are pre-existing and unrelated to any final-project change: Starlette
  deprecating its httpx TestClient, and the `HTTP_422_UNPROCESSABLE_ENTITY`
  constant rename. No test fails.

## CI evidence

- **Workflow file:** `.github/workflows/ci.yml`.
- **Latest run link or note:** run **#14** on the `final-project` branch
  (commit `607bcad`) finished **Success** in 24s total, with the `test` job
  green in 21s. The workflow runs `pytest` on every push (any branch) and every
  pull request. It has also run green on prior pushes to `main` during Module 4,
  including a deliberate red-then-green break-test cycle proving the pipeline can
  fail. (One non-fatal annotation on run #14 is a GitHub-platform Node.js runtime
  deprecation for the setup actions - it does not affect the test result.)
- **Test command used by CI:** `pytest` (plain, after
  `pip install -r requirements.txt` on a pinned Python `3.14`).
- **Shortcut check:** no `continue-on-error`, no `|| true`, `pytest` is not
  skipped, and the Python version is exact (`3.14`), not a range. Confirmed by
  reading `.github/workflows/ci.yml`.

## Docker evidence

- **Build command:** `docker build -t task-tracker .`
  (succeeded in ~16s on `python:3.12-slim`, image `task-tracker:latest`).
- **Run command:** `docker run -d --name tt -p 8000:8000 task-tracker`.
- **/health check:** the container returned HTTP 200 with
  `{"status":"ok","timestamp":"2026-07-29T19:18:14.815247+00:00"}`.
- **Non-root check:** `docker exec tt whoami` returned `app` (uid 1000), so the
  process does not run as root.
- **No-baked-secrets check:** `.dockerignore` excludes `.env` and `.env.*`, and
  the Dockerfile copies only `app/` (`COPY --chown=app:app app ./app`) - no
  `.env`, `.git`, tests, docs, or frontend enter the image. Runtime command is
  `uvicorn app.main:app --host 0.0.0.0 --port 8000` with no `--reload`.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README says the suite has "30 tests". | Ran `python -m pytest`. | Accurate: `30 passed`. | None. |
| `/health` returns `{"status":"ok", ...}` (README + `app/api/health.py`). | `curl http://127.0.0.1:8000/health` against both uvicorn and the container. | Accurate: 200 with `status: ok` and a UTC timestamp, in both. | None. |
| README "Run with Docker" claims a non-root user and a `/health` healthcheck. | `docker build` + `docker run`, then `docker exec tt whoami` and `curl /health`. | Accurate: `whoami` = `app`, container `/health` = 200. | None. |
| Endpoints table: an invalid status transition (e.g. `ToDo -> Done`) returns 422. | `test_patch_invalid_transition_todo_to_done_returns_422` in the passing suite. | Accurate: the test passes, so the 422 contract holds. | None. |
