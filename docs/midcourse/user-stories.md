# User Stories - Mid-Course Feature Sprint

Two features added to the Task Tracker: **due dates + overdue filter** and
**search + combined filters**. Statuses are `ToDo` / `InProgress` / `Done`;
priorities are `High` / `Medium` / `Low`.

## Feature 1 - Due dates + overdue filter

**US1.1 - Set a due date**
As a user, I want to give a task an optional due date so I can track deadlines.
- Create and edit accept an optional `due_date` in `YYYY-MM-DD` form.
- An invalid date string is rejected with 422.
- The due date shows on the card and in the edit modal.

**US1.2 - See overdue tasks**
As a user, I want overdue tasks flagged so I can act on them first.
- A task whose due date is before today and is **not Done** shows an "Overdue" indicator.
- A task with no due date, a future due date, or a Done status is never marked overdue.

**US1.3 - Filter to only overdue**
As a user, I want to view only overdue tasks.
- `GET /tasks?overdue=true` returns only overdue tasks.
- The board has an "Overdue only" toggle that applies the same filter.
- No overdue tasks returns 200 with an empty board (three columns still visible).

**US1.4 - Update or clear a due date**
As a user, I want to change or remove a due date.
- `PATCH /tasks/{id}` with a new `due_date` updates it and returns 200.
- Clearing the field in the modal sends `null` and removes the date.

> **AI assumption I corrected:** the first implementation treated *any* past-due
> task as overdue, including completed ones. I corrected the rule so a Done task
> past its due date is **not** overdue - finished work should not be flagged.

## Feature 2 - Search + combined filters

**US2.1 - Search by text**
As a user, I want to search tasks by text so I can find them quickly.
- `search` matches a case-insensitive substring of the title **or** description.
- No match returns 200 with `[]` (an empty board, not a 404).

**US2.2 - Combine filters**
As a user, I want to combine search with status, priority and overdue.
- All filters combine with AND.
- Combining `status` + `priority` returns only tasks matching both.

**US2.3 - Keep the board usable while filtering**
As a user, I want the board to stay readable when a filter matches little.
- All three columns remain visible with "No tasks" placeholders.
- An invalid `status` or `priority` filter value returns 422.

**US2.4 - Clear filters**
As a user, I want to reset all filters in one click.
- A "Clear" button resets the controls and reloads the full board.

> **AI assumption I corrected:** the AI first proposed filtering on the frontend
> (fetch all tasks, filter in JavaScript). I corrected it to filter in the
> backend via `GET /tasks` query params, so the behavior is testable with pytest
> and matches the project brief.
