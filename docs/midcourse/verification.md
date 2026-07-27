# Verification - Mid-Course Feature Sprint

## Baseline (before changes)
On the `main` branch (Module 3.5 state), `python -m pytest` reported
**22 passed**. That is the checkpoint the `mid-course-project` branch was cut
from.

## Backend tests (after changes)
`python -m pytest` reports **30 passed** - the 22 existing tests plus **8 new**
tests:

Feature 1 (due dates + overdue):
- `test_create_task_with_valid_due_date_returns_201`
- `test_create_task_invalid_due_date_format_returns_422`
- `test_update_task_due_date_returns_200`
- `test_overdue_filter_returns_only_overdue_tasks`

Feature 2 (search + combined filters):
- `test_search_matches_title_and_description`
- `test_combined_status_and_priority_filter`
- `test_search_no_match_returns_200_and_empty_list`
- `test_invalid_filter_value_returns_422`

## Manual browser checks
Backend on `:8000`, frontend served over HTTP on `:5500`.

- Due date shows on the card ("Due 2026-08-01") and in the edit modal.
- A past-due, not-Done task shows a red **Overdue** pill; a past-due **Done**
  task shows the date but **no** pill (verified with a seeded Done task).
- "Overdue only" toggle returns only the overdue task.
- Priority filter and text search each narrow the board; combining search + a
  priority returns the intersection.
- A no-match search leaves all three columns visible with "No tasks"
  placeholders (empty state preserved), board still shown.
- Creating a task with a due date persists it and renders it on the card.

## Behavior contract - after the feature work
The full contract (`frontend/BEHAVIOR_CONTRACT.md`) was re-run after adding both
features. All items still pass: three columns and counts, priority sort, all
four UI states, valid drag persists / invalid drag reverts with a message,
same-column drag sends no PATCH, and all five modal flows (empty-title blocked
with no request, create, edit reorders, invalid transition keeps the modal open,
and every dismissal path). The feature code was kept small and self-contained,
so no refactor was required to keep it clean; the contract-preserving
"checkpoint → refactor → re-verify" loop was demonstrated in Module 3.4, and if
a focused refactor is applied here the same contract is the check to re-run
afterward.

## Break Test evidence (two tests)

### 1. `test_overdue_filter_returns_only_overdue_tasks`
Broke `is_overdue` by dropping the "not Done" exclusion
(`return task.due_date < today`). The past-due Done task was then wrongly
counted as overdue:

```
>       assert len(data) == 1
E       AssertionError: assert 2 == 1
FAILED tests/test_tasks.py::test_overdue_filter_returns_only_overdue_tasks
```

Restored the exclusion → the test passes again.

### 2. `test_search_matches_title_and_description`
Broke the search filter to match the title only (dropped the description
branch). The task that matched only via its description disappeared:

```
>       assert titles == {"Deploy release", "Write docs"}
E       AssertionError: assert {'Deploy release'} == {'Deploy rele... 'Write docs'}
FAILED tests/test_tasks.py::test_search_matches_title_and_description
```

Restored the description branch → the test passes again.

After both break tests and restores, `python -m pytest` → **30 passed**.
