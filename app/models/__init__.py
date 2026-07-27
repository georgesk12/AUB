"""Task Tracker data models (Module 2, Part 2.1).

Built to the Module 2 Prompt Library "A1" spec: Pydantic v2 only, exact enum
values, strict title validation, and extra="forbid" so unknown or
server-owned fields are rejected.

Note on layout: the Module 1 skeleton ships `app/models` as a *package*
(this directory). A separate top-level `app/models.py` module would be
shadowed by this package, so the models live here in the package __init__.
`from app.models import TaskCreate, ...` resolves to this file - identical
to importing from an app/models.py module.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStatus(str, Enum):
    """Allowed task columns on the Kanban board."""

    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    """Allowed priority levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def _clean_title(value: str) -> str:
    """Strip surrounding whitespace, reject blank or over-200-char titles."""
    trimmed = value.strip()
    if not trimmed:
        raise ValueError("title must not be empty or whitespace only")
    if len(trimmed) > 200:
        raise ValueError("title must be at most 200 characters")
    return trimmed


class TaskCreate(BaseModel):
    """Client input for creating a task. Server-owned fields are NOT accepted."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None   # ISO date (YYYY-MM-DD); optional

    @field_validator("title")
    @classmethod
    def _validate_title(cls, v: str) -> str:
        return _clean_title(v)


class TaskUpdate(BaseModel):
    """Partial update. Every field optional; id/timestamps are NOT accepted."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def _validate_title(cls, v: Optional[str]) -> Optional[str]:
        # Only validate when a title is actually provided.
        if v is None:
            return v
        return _clean_title(v)


class TaskResponse(BaseModel):
    """Server representation returned to clients. id + timestamps included."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
