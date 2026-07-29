# Security Review - Module 5.2

This review is a docs-only Module 5 artifact. No application code was changed.
The posture here is not "accept the audit"; it is to grade it. Each finding is
classified as **Valid**, **False Positive**, or **Noise**, then reconciled with a
manual scan.

## Scope And Files Inspected

- `app/main.py` - routes, CORS, API behavior.
- `app/models/__init__.py` - Pydantic models and validation.
- `app/storage.py` - in-memory storage, filtering, overdue logic.
- `app/business_rules.py` - status-transition validation.
- `frontend/index.html` - browser rendering, fetch calls, modal, drag/drop.
- `requirements.txt` - dependency declarations.
- `.github/workflows/ci.yml` - CI behavior.
- `Dockerfile` and `.dockerignore` - container build and runtime image.
- `.gitignore`, `app/core/config.py`, `app/api/health.py` - secrets/config and health behavior.

## Graded Findings

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Grade | Reason |
|---|---|---|---|---|---|---|---|
| S1 | High if deployed publicly; Low in course scope | `app/main.py:18-26`, `README.md` | No authentication or authorization protects task CRUD endpoints. | The FastAPI app description explicitly says "no authentication"; all task routes in `app/main.py` are public handlers. | Keep as a course-scope decision. If this ever becomes real software, add auth, ownership checks, and tests before deployment. | Valid | Intentional for the course, but a real production risk. This is not a code bug in the learning repo. |
| S2 | Medium | `app/models/__init__.py:53-58`, `app/storage.py:21-23` | `description` and `assignee` are unbounded strings in an in-memory store. | `title` is capped at 200, but `description` and `assignee` have no length constraints; `_tasks` stores everything in memory. | Backlog: add modest max lengths for description and assignee, then tests for overlong values. | Valid | Concrete denial-of-service / oversized-response risk, especially because storage is process memory. |
| S3 | Low to Medium | `app/main.py:92-127`, `app/storage.py:81-119` | `search` and `assignee` query params are unbounded and run over every in-memory task. | `search` is accepted as `str | None`, then lowercased and matched against title/description for every task. | Backlog: cap search/assignee query length and consider pagination if task count grows. | Valid | Real but limited by the learning app's small in-memory scope. |
| S4 | Medium in production; Low locally | `app/main.py:31-35` | CORS allows any localhost or 127.0.0.1 port and all methods/headers. | `allow_origin_regex` permits localhost/127.0.0.1 on any port; `allow_methods=["*"]`, `allow_headers=["*"]`. | Keep for local dev. If deployed, replace with explicit trusted origins. | Valid | Correct for local frontend work, but too broad for deployed environments. |
| S5 | Medium | `requirements.txt:5-13`, `.github/workflows/ci.yml:24-30` | Dependencies use lower-bound pins only, so CI may install newer versions than previously tested. | Requirements are `fastapi>=0.115`, `uvicorn>=0.32`, etc.; CI installs with `pip install -r requirements.txt`. | Backlog: add a lockfile or constraints file for reproducible CI/builds. | Valid | Supply-chain/reproducibility risk. Not urgent for the course, but worth recording. |
| S6 | Low | `app/main.py:145-148`, `app/main.py:180-183`, `app/main.py:214-217`, `app/business_rules.py:41-46` | Error details echo caller-supplied task IDs and status values. | 404 details include the submitted `task_id`; 422 transition detail includes current/new status and allowed transitions. | Keep as acceptable for this API. Avoid putting secrets or internal paths in future error messages. | Noise | Technically true, but task IDs/statuses are not sensitive here and the messages improve API usability. |
| S7 | Low | `frontend/index.html:430-475`, `frontend/index.html:615-690` | Frontend could be vulnerable to XSS if it rendered task fields as HTML. | Actual code uses `textContent` for title, description, assignee, due date, error messages, and toast text. | No action. Continue using `textContent` rather than `innerHTML` for user data. | False Positive | The risky pattern is absent; the implementation uses safe DOM text assignment. |
| S8 | Low | `.gitignore:11-12`, `.dockerignore:16-19`, `app/core/config.py:23-28` | Local `.env` exists and settings load from it. | `.env` is ignored by git; `.dockerignore` excludes `.env` and `.env.*`; only `.env.example` is tracked. | No action unless real secrets are accidentally added to `.env.example`. | False Positive | Local `.env` is expected and is excluded from git and Docker. I did not inspect or quote its contents. |
| S9 | Informational | `Dockerfile:24-53`, `.dockerignore:21-31` | Docker runtime should avoid root, reload mode, and excess files. | Runtime image uses `python:3.12-slim`, creates `app` user, switches to `USER app`, copies only `app/`, and runs uvicorn without `--reload`. | No action. These are positive controls to keep. | Noise | This is not a finding; it is a confirmed clean category. |

## Categories With No Finding

- **SQL injection:** not applicable. There is no SQL, ORM, or database.
- **Server-owned fields:** clean. `TaskCreate` / `TaskUpdate` forbid extras and do not include `id`, `created_at`, or `updated_at`.
- **Status transition trust:** clean. The backend validates `(current, new)` pairs before update.
- **Frontend HTML injection:** clean. User-controlled task fields are rendered with `textContent`.
- **Docker privilege:** clean. Runtime drops to a non-root user and excludes docs/tests/frontend/secrets.
- **Committed secrets:** no tracked `.env`; secret-key scan found no obvious token material in tracked source.

## Manual Scan Notes

### Input Validation

The strongest issue is uneven field sizing. Title is capped and stripped, but
description and assignee are not capped. The course app is intentionally small,
yet the API accepts arbitrary-length strings and keeps them in memory. This is
the most practical security backlog item because it is simple to fix and simple
to test.

### Authorization

No authentication is intentional and documented. I would not "fix" it inside
this course repo. I would, however, treat it as a hard blocker before any real
deployment, because every caller can create, read, update, and delete every
task.

### Data Exposure

The API exposes task data to any caller because there is no auth. Aside from
that deliberate limitation, it does not expose stack traces, filesystem paths,
secrets, or raw config values in normal responses.

### Error Handling

Errors are mostly FastAPI/Pydantic-generated 422s plus explicit 404s and
transition 422s. Messages are readable and do not include sensitive internals.
The transition message reveals the allowed transition list, but that is part of
the public business contract.

### Dependencies, CI, And Docker

CI runs the tests without failure-swallowing flags. Docker uses a non-root
runtime and a small copy set. The main remaining risk is reproducibility:
dependencies are lower-bound pins, not a locked set.

## Reconciliation

### Agreement: AI And Manual Scan

- No auth is intentional for the course but production-risky.
- Unbounded non-title text fields are the most concrete application-level risk.
- CORS is correct for local development and would need tightening for deployment.
- Dependency lower-bound pins are a reproducibility/supply-chain concern.

### AI-Only Or Mostly AI-Pattern Findings

- Generic "XSS risk" is a false positive once `frontend/index.html` is read:
  user-controlled fields use `textContent`, not `innerHTML`.
- Generic "Docker may run as root" is also false: the Dockerfile switches to
  `USER app`.

### You-Only / Manual Findings

- The local `.env` exists but is intentionally ignored. This should be handled
  carefully in governance notes: never paste its contents into AI tools, and do
  not treat `.env.example` as secret unless it stops being placeholder-only.
- `search` and `assignee` query strings are also unbounded. That is easier to
  miss than body-field size limits because the values are not stored directly,
  but they still drive per-task work on every request.

## Top 3 Security Backlog

1. **Add max lengths for `description` and `assignee`.**
   - Why first: simple, testable, and directly tied to in-memory storage risk.
   - Suggested tests: overlong description returns 422; overlong assignee returns 422.

2. **Add max lengths for `search` and `assignee` query params.**
   - Why second: prevents oversized query work and keeps the API contract tidy.
   - Suggested tests: overlong `search` returns 422; normal search still works.

3. **Add dependency constraints or a lockfile.**
   - Why third: reduces "works yesterday, breaks today" CI/build drift.
   - Suggested path: generate a constraints file and document the update process.

## Final Judgment

For a course learning project, the security posture is acceptable: validation is
strict where the core model needs it, server-owned fields stay server-owned, the
frontend avoids obvious injection patterns, CI runs tests, and Docker has sane
runtime defaults.

For production, the app is not ready. The absence of authentication, broad local
CORS pattern, in-memory storage, unbounded secondary fields, and unlocked
dependencies would need to be addressed before exposing it beyond a local demo.

