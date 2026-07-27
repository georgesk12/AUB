"""Deprecated location.

The Module 1 sketch that lived here has been replaced by the Module 2 data
models, which now live in app/models/__init__.py (the models package).
Import them from `app.models`, e.g. `from app.models import TaskCreate`.

This file is kept only so nothing that referenced app.models.task breaks;
it re-exports the models from the package.
"""

from app.models import (  # noqa: F401
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)
