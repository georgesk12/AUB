"""Task Tracker API - application entry point.

Creates the FastAPI app, applies CORS for the local frontend, and defines the
task routes. Storage is in-memory (no database) and there is no authentication
- this is a learning project. The full HTTP contract (routes, status codes and
filters) is documented on each handler below and rendered at ``/docs``.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.api import health
from app.business_rules import validate_status_transition
from app.core.config import settings
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "A small task tracker REST API: create, list/filter, read, update "
        "(with status-transition rules) and delete tasks. In-memory storage, "
        "no authentication."
    ),
)

# CORS: the frontend is served from a different local origin (e.g. Live Server
# on :5500), so the browser needs the backend to allow it. Scoped to
# localhost / 127.0.0.1 on any port - local development only.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers. The health check lives in its own module.
app.include_router(health.router)


@app.get("/", tags=["root"])
def root() -> dict:
    """Landing payload pointing callers at the docs and health check.

    Returns:
        dict: The app name, environment, and the ``/docs`` and ``/health`` paths.
    """
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
        "docs": "/docs",
        "health": "/health",
    }


# --------------------------------------------------------------------------
# Task CRUD endpoints. Each route delegates to the storage layer; ids and
# timestamps are generated in storage, input validation is handled by
# Pydantic, and a missing task raises 404.
# --------------------------------------------------------------------------


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a task.

    Args:
        payload: The new task. ``title`` is required; ``status`` and
            ``priority`` default to ``ToDo`` and ``Medium``.

    Returns:
        TaskResponse: The created task, with a generated id and timestamps
            (HTTP 201).

    Raises:
        HTTPException: 422 (via Pydantic) if the title is missing, blank or
            over 200 characters, an enum value is invalid, or an unknown field
            is sent.

    Example:
        ``POST /tasks {"title": "Ship release", "priority": "High"}`` -> 201.
    """
    return storage.add_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee: str | None = None,
    search: str | None = None,
    overdue: bool | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered. All filters combine with AND.

    Args:
        status: Keep only tasks with this status.
        priority: Keep only tasks with this priority.
        assignee: Case-insensitive exact match on the assignee.
        search: Case-insensitive substring of the title OR description.
        overdue: ``true`` keeps only overdue tasks (due date before today and
            not Done); ``false`` keeps only non-overdue.

    Returns:
        list[TaskResponse]: The matching tasks. An empty result is HTTP 200
            with ``[]`` (never a 404).

    Raises:
        HTTPException: 422 (via FastAPI) if ``status`` or ``priority`` is not a
            valid enum value.

    Example:
        ``GET /tasks?search=deploy&priority=High`` -> 200 with the matches.
    """
    return storage.get_all_tasks(
        status=status,
        priority=priority,
        assignee=assignee,
        search=search,
        overdue=overdue,
    )


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Retrieve a single task by id.

    Args:
        task_id: The task's id.

    Returns:
        TaskResponse: The task (HTTP 200).

    Raises:
        HTTPException: 404 if no task has this id.
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update a task, enforcing status-transition rules.

    Only the fields present in the body are changed. When ``status`` is
    supplied, the change is validated against the allowed transitions
    (ToDo->InProgress, InProgress->Done, Done->InProgress); a title-only or
    other partial update skips transition validation entirely.

    Args:
        task_id: The task's id.
        payload: The fields to change (any subset of the editable fields).

    Returns:
        TaskResponse: The updated task (HTTP 200).

    Raises:
        HTTPException: 404 if the task does not exist; 422 for an invalid
            status transition, or (via Pydantic) an invalid field value.

    Example:
        ``PATCH /tasks/{id} {"status": "InProgress"}`` on a ToDo task -> 200;
        ``{"status": "Done"}`` on a ToDo task -> 422.
    """
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        # Check existence BEFORE validating, so a missing task is a 404.
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )
        validate_status_transition(existing.status, payload.status)

    updated = storage.update_task(task_id, payload)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return updated


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
)
def delete_task(task_id: str) -> None:
    """Delete a task.

    Args:
        task_id: The task's id.

    Returns:
        None: HTTP 204 with an empty body on success (no JSON payload).

    Raises:
        HTTPException: 404 if no task has this id.
    """
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return None


if __name__ == "__main__":
    # Allows `python -m app.main` as an alternative to the uvicorn CLI.
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=settings.port,
        reload=True,
    )
