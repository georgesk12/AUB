"""In-memory storage layer for the Task Tracker.

A single module-level dict (``_tasks``) keyed by string id is the whole store;
there is no database and no ORM. IDs (UUID strings) and the ``created_at`` /
``updated_at`` timestamps are generated HERE, not in the routes, so the client
can never set them. The store is process-local and cleared on restart, which is
intentional for this learning project.

Public functions: :func:`add_task`, :func:`get_all_tasks` (with AND-combined
filters), :func:`get_task_by_id`, :func:`update_task`, :func:`delete_task`, and
the pure helper :func:`is_overdue`. :func:`_reset` clears the store for tests.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

# Module-level in-memory store. Not thread-safe; fine for a single-process
# learning project.
_tasks: dict[str, TaskResponse] = {}


def _now() -> datetime:
    """Current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def is_overdue(task: TaskResponse, today: Optional[date] = None) -> bool:
    """Report whether a task is overdue.

    A task is overdue when it has a ``due_date`` strictly before ``today`` and
    its status is not ``Done``. This is computed on every call (never stored),
    so it always reflects the current date and the task's latest status.

    Args:
        task: The task to check.
        today: The reference date. Defaults to ``date.today()``; passed
            explicitly by tests for determinism.

    Returns:
        bool: ``True`` if the task is overdue, otherwise ``False``. A task with
            no ``due_date`` is never overdue.
    """
    if task.due_date is None:
        return False
    if today is None:
        today = date.today()
    return task.due_date < today and task.status != TaskStatus.DONE


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and store a task, assigning a new id and timestamps.

    Args:
        payload: The validated new-task fields. ``description`` defaults to an
            empty string when omitted.

    Returns:
        TaskResponse: The stored task, with a server-generated UUID ``id`` and
            equal ``created_at`` / ``updated_at`` UTC timestamps.
    """
    now = _now()
    task = TaskResponse(
        id=str(uuid.uuid4()),
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        created_at=now,
        updated_at=now,
    )
    _tasks[task.id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee: Optional[str] = None,
    search: Optional[str] = None,
    overdue: Optional[bool] = None,
) -> list[TaskResponse]:
    """Return tasks, optionally filtered. All filters combine with AND.

    Args:
        status: Exact enum match on status.
        priority: Exact enum match on priority.
        assignee: Case-insensitive exact match on the assignee.
        search: Case-insensitive substring of the title OR description. An
            empty string is ignored (no filtering).
        overdue: ``True`` keeps only overdue tasks, ``False`` keeps only
            non-overdue; ``None`` applies no overdue filter.

    Returns:
        list[TaskResponse]: The matching tasks, in insertion order. An empty
            list when nothing matches (never ``None``).
    """
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [t for t in tasks if t.status == status]
    if priority is not None:
        tasks = [t for t in tasks if t.priority == priority]
    if assignee is not None:
        tasks = [t for t in tasks if (t.assignee or "").lower() == assignee.lower()]
    if search:
        q = search.lower()
        tasks = [
            t for t in tasks
            if q in t.title.lower() or q in (t.description or "").lower()
        ]
    if overdue is not None:
        today = date.today()
        tasks = [t for t in tasks if is_overdue(t, today) == overdue]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Return the task with this id, or None if it does not exist."""
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to a stored task.

    Only the fields the client actually sent (``exclude_unset``) are applied,
    and ``updated_at`` is refreshed only when at least one field changes. This
    function does NOT enforce status-transition rules - the route validates the
    transition before calling here.

    Args:
        task_id: The id of the task to update.
        payload: The fields to change (any subset of the editable fields).

    Returns:
        Optional[TaskResponse]: The updated task, or ``None`` if no task has
            this id.
    """
    existing = _tasks.get(task_id)
    if existing is None:
        return None

    # Only the fields the client actually sent are applied.
    changes = payload.model_dump(exclude_unset=True)
    if changes:
        data = existing.model_dump()
        data.update(changes)
        data["updated_at"] = _now()
        existing = TaskResponse(**data)
        _tasks[task_id] = existing
    return existing


def delete_task(task_id: str) -> bool:
    """Delete a task. Returns True if it existed, False otherwise."""
    return _tasks.pop(task_id, None) is not None


def _reset() -> None:
    """Clear all tasks. For tests only."""
    _tasks.clear()
