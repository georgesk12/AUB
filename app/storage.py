"""In-memory storage layer for the Task Tracker (Module 2, Part 2.1).

Built to the Module 2 Prompt Library "A1" spec. A module-level dict keyed by
string id. IDs and timestamps are generated HERE, not in the routes. No
database and no ORM - swapped for real persistence in a later module.
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
    """A task is overdue if it has a due date before today and is not Done.

    Overdue is computed here (not stored) so it always reflects the current
    date and the task's latest status.
    """
    if task.due_date is None:
        return False
    if today is None:
        today = date.today()
    return task.due_date < today and task.status != TaskStatus.DONE


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and store a task, assigning a new id and timestamps."""
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

    - status / priority: exact enum match
    - assignee: case-insensitive exact match
    - search: case-insensitive substring of title OR description
    - overdue: True = only overdue, False = only not-overdue
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
    """Apply a partial update. Returns None if the task does not exist."""
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
