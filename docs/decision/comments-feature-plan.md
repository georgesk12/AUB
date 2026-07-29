# Comments Feature Plan - Module 5.4

This is a planning artifact only. No comments feature was implemented, and no
application code was changed.

The exercise is to compare a generic assistant plan with a repo-grounded coding
agent plan. The feature idea is: add comments to tasks.

## Generic Plan

A generic plan for comments in a task tracker would usually look like this:

1. Define a `Comment` data model with `id`, `task_id`, `author`, `body`,
   `created_at`, and `updated_at`.
2. Add validation schemas for creating and updating comments.
3. Add storage behavior for comments.
4. Add API endpoints:
   - `POST /tasks/{task_id}/comments`
   - `GET /tasks/{task_id}/comments`
   - `PATCH /comments/{comment_id}`
   - `DELETE /comments/{comment_id}`
5. Return 404 when a task or comment does not exist.
6. Add frontend UI for showing, creating, editing, and deleting comments.
7. Add tests and documentation.

**Critique label: Generic but incomplete.**

This is coherent, but it is not yet a project plan. It does not know this repo
uses process-local in-memory storage, Pydantic v2 models in a package
`__init__.py`, vanilla JavaScript in one HTML file, no authentication, no
database migrations, and pytest fixtures that reset storage before and after
each test.

## Repo-Grounded Plan

### 1. Scope Decision

Add task-scoped comments to the existing learning app:

- A comment belongs to exactly one task.
- Comments are stored in memory, like tasks.
- There is no user system, so `author` is a free-text optional field rather
  than a foreign key.
- Server-owned fields are `id`, `task_id`, `created_at`, and `updated_at`.
- The feature should not introduce auth, a database, an ORM, migrations, a
  frontend framework, or an external service.

**Critique label: Grounded and correct.**

This matches the constraints in `AGENTS.md`, `app/main.py`, and `app/storage.py`.
The no-auth choice is intentional course scope, not something to solve inside
this feature.

### 2. Data Model

Add comment models beside the task models in `app/models/__init__.py`, following
the existing Pydantic v2 style:

- `CommentCreate`
  - `body: str`
  - `author: Optional[str] = None`
  - `extra="forbid"`
- `CommentUpdate`
  - `body: Optional[str] = None`
  - `author: Optional[str] = None`
  - `extra="forbid"`
- `CommentResponse`
  - `id: str`
  - `task_id: str`
  - `body: str`
  - `author: Optional[str]`
  - `created_at: datetime`
  - `updated_at: datetime`

Validation should mirror the task-title discipline:

- `body` is required on create.
- `body` is stripped and cannot be blank.
- `body` should have a max length, for example 1000 characters.
- `author`, if present, should be stripped and capped, for example 100
  characters.

**Critique label: Grounded with one design choice.**

The placement and validation style match `TaskCreate`, `TaskUpdate`, and
`TaskResponse`. The exact max lengths are a product decision; they should be
chosen before implementation and then tested.

### 3. Storage Layer

Extend `app/storage.py` rather than adding a database:

- Add `_comments: dict[str, CommentResponse] = {}`.
- Add `add_comment(task_id, payload)`.
- Add `get_comments_for_task(task_id)`.
- Add `get_comment_by_id(comment_id)`.
- Add `update_comment(comment_id, payload)`.
- Add `delete_comment(comment_id)`.
- Update `_reset()` to clear both `_tasks` and `_comments`.

`add_comment` should not create comments for missing tasks. Either the route
checks task existence before calling storage, or storage returns `None` if the
task is absent. Pick one convention and keep it consistent.

When a task is deleted, its comments should also be deleted to avoid orphaned
comments in memory.

**Critique label: Grounded and requires explicit orphan behavior.**

The storage plan fits the existing module-level dict pattern. The important
repo-specific detail is delete behavior: `delete_task()` currently removes only
the task, so comments need a cascade decision.

### 4. API Routes

Add routes in `app/main.py` near the existing task routes:

- `POST /tasks/{task_id}/comments`
  - Body: `CommentCreate`
  - Response: `CommentResponse`
  - Status: 201
  - 404 if the task does not exist.
- `GET /tasks/{task_id}/comments`
  - Response: `list[CommentResponse]`
  - Status: 200
  - 404 if the task does not exist.
  - Empty comments for an existing task returns `[]`, not 404.
- `PATCH /comments/{comment_id}`
  - Body: `CommentUpdate`
  - Response: `CommentResponse`
  - Status: 200
  - 404 if the comment does not exist.
- `DELETE /comments/{comment_id}`
  - Status: 204
  - 404 if the comment does not exist.

Do not add route-level auth or ownership checks inside this course feature,
because the base API has no authentication.

**Critique label: Grounded and consistent.**

This follows the existing status-code contract in `app/main.py`: create returns
201, list returns 200 with empty lists, patch returns 200, delete returns 204,
and missing resources return 404.

### 5. Frontend Behavior

Update `frontend/index.html` only after the backend contract is tested:

- Show a compact comment count on each card.
- In the edit modal, add a comments area for the selected task.
- Fetch comments when opening edit mode, not for every card on every board
  render.
- Allow adding a comment from the modal.
- Optionally allow deleting a comment from the modal.
- Keep all comment text rendered with `textContent`, following the current safe
  card-rendering pattern.
- Keep invalid task status transitions handled exactly as they are now; comments
  should not interfere with status editing.

Update `frontend/BEHAVIOR_CONTRACT.md` with comment-specific checks before any
large frontend refactor.

**Critique label: Grounded with sequencing caution.**

The frontend is a single vanilla JS file with existing modal logic. A generic
plan might propose React components or a route-based UI, but this repo should
extend the current DOM-building style unless the project scope changes.

### 6. Tests

Add tests to `tests/test_tasks.py` or split to `tests/test_comments.py` if the
file gets too large. Use the existing `client` fixture and the autouse storage
reset from `tests/conftest.py`.

Minimum backend tests:

- Create a comment for an existing task returns 201 with server fields.
- Create a comment for a missing task returns 404.
- Create a blank comment body returns 422.
- List comments for an existing task with none returns 200 and `[]`.
- List comments returns only comments for that task.
- Patch comment body returns 200 and updates `updated_at`.
- Patch missing comment returns 404.
- Delete comment returns 204 with empty body.
- Delete missing comment returns 404.
- Deleting a task removes that task's comments.
- Unknown fields in comment create/update return 422.

Optional break tests:

- Break blank-body validation and confirm the blank-body test fails.
- Break task-scoping in list comments and confirm cross-task comments leak into
  the response.
- Break cascade delete and confirm orphan comments remain visible or retrievable.

**Critique label: Grounded and testable.**

The tests match the existing pytest style: behavior-first names, no database
fixtures, and direct API calls through FastAPI `TestClient`.

### 7. Documentation

Update these docs only after implementation:

- `README.md`: add comments endpoints and a short usage example.
- `frontend/BEHAVIOR_CONTRACT.md`: add comment display/create/delete checks.
- `docs/security-review.md`: mention comment-body length limits and XSS
  rendering constraints if the feature is implemented.
- `AGENTS.md`: add comment business rules if the feature becomes part of the
  repo contract.

**Critique label: Grounded and deferred.**

Documentation should describe the code after the feature exists. For Part 5.4,
this planning doc is the deliverable; README/API docs should not be updated yet
because comments do not exist.

## Biggest Differences: Generic vs Repo-Grounded

| Area | Generic plan | Repo-grounded plan |
|---|---|---|
| Persistence | Might assume SQL tables and migrations. | Uses `app/storage.py` module-level dicts because this repo has no database. |
| Models | Might create a new schemas folder. | Extends `app/models/__init__.py`, where current Pydantic models live. |
| Authorship | Might assume users/auth. | Uses optional free-text `author` because the API has no auth. |
| Frontend | Might assume components or a framework. | Extends the single-file vanilla JS modal/card pattern. |
| Tests | Might talk vaguely about unit/integration tests. | Names FastAPI `TestClient` tests and the existing storage reset fixture. |
| Scope | Might silently upgrade the app architecture. | Preserves course constraints and avoids implementation during planning. |

## Recommended Implementation Sequence

1. Add comment models and validation.
2. Add in-memory comment storage functions and `_reset()` cleanup.
3. Add API routes one at a time with tests after each route group.
4. Add cascade delete behavior and tests.
5. Update frontend modal comment display/create/delete behavior.
6. Update README, behavior contract, and AGENTS guidance.

## Do Not Implement Yet

For Module 5.4, the correct endpoint is this plan. Implementation should wait
until the user explicitly asks for comments to be built.

