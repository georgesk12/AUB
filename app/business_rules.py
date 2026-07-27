"""Business rules for the Task Tracker (Module 2.3).

Status-transition validation. A setter that writes any status is not a
business rule - the rule is about which (current -> new) pairs are allowed.
The rules live in a frozenset (not an if/elif chain) so they are one line
to extend later, and same->same is rejected implicitly because it is not in
the set.

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
    """Raise 422 unless (current, new) is an allowed transition.

    Same -> same is invalid. Anything not in VALID_TRANSITIONS is invalid.
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
