"""Application entry point.

Creates the FastAPI app, wires in the routers, and (when run directly)
starts the uvicorn server on the configured port. No authentication and no
database - intentional for this learning skeleton.

Module 2.2: the five CRUD endpoints for /tasks are defined here, one strict
route each (specs B1-B2.4). Business rules (status transitions) come in 2.3.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.api import health
from app.business_rules import validate_status_transition
from app.core.config import settings
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

# The FastAPI instance. `title` and `version` show up in the /docs page.
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Learning-project task tracker (Module 2).",
)

# CORS: the frontend (Module 3) is served from a different local origin
# (e.g. Live Server on :5500), so the browser needs the backend to allow it.
# Scoped to localhost / 127.0.0.1 on any port - local development only.
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
    """Friendly landing payload pointing users at the docs."""
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
        "docs": "/docs",
        "health": "/health",
    }


# --------------------------------------------------------------------------
# Task CRUD endpoints (Module 2.2). Each route delegates to the storage layer;
# ids and timestamps are generated in storage, validation is handled by
# Pydantic, and missing tasks raise 404.
# --------------------------------------------------------------------------


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(payload: TaskCreate) -> TaskResponse:
    # Invalid input (missing/blank/overlong title, bad enum, unknown field)
    # is rejected by Pydantic with 422 before we get here.
    return storage.add_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[TaskResponse]:
    # An empty result is a valid 200 with [], not a 404.
    return storage.get_all_tasks(status=status, priority=priority)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    # Business rule (2.3): only validate a transition when a new status is
    # supplied. Title-only / partial updates skip this entirely.
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
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    # 204: no response body.
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
