"""Business rules for the Task Tracker: status-transition validation.

The rule is about which ``(current -> new)`` status pairs are allowed, so the
allowed pairs live in a ``frozenset`` (``VALID_TRANSITIONS``) rather than an
if/elif chain - it is one line to extend, and same->same is rejected implicitly
because it is not in the set.

Allowed:  ToDo -> InProgress, InProgress -> Done, Done -> InProgress (reopen)
Rejected: ToDo -> Done (skips work), Done -> ToDo (revert), and same -> same
"""
from fastapi import HTTPException, status

from app.models import TaskStatus

VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset(
    {
        (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
        (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
        (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
    }
)


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Validate a status change, raising on a disallowed transition.

    Args:
        current: The task's current status.
        new: The requested new status.

    Returns:
        None: Returns nothing when the transition is allowed.

    Raises:
        HTTPException: 422 if ``(current, new)`` is not in
            ``VALID_TRANSITIONS``. Same -> same is always invalid. The error
            detail lists the allowed transitions.
    """
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid status transition from {current.value} to "
                f"{new.value}. Allowed transitions: {allowed}"
            ),
        )
