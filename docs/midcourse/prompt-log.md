# Prompt Log - Mid-Course Feature Sprint

Assistant used: **Claude (Cowork)** as a file-aware editor assistant - it reads
and edits the real project files and runs the verifications. Each prompt below
notes what it returned and what I accepted, edited, or rejected.

## Feature 1 - Due dates + overdue filter

### Prompt 1.1 (weak → strong)
**Weak:** "add due dates to the tasks"
Returned a broad change across models, storage and routes and guessed a
`datetime` with a time component and a made-up date format. **Rejected** - too
broad to review and wrong granularity.

**Strong rewrite:** "In `app/models/__init__.py`, add an optional
`due_date: Optional[date] = None` field to `TaskCreate`, `TaskUpdate` and
`TaskResponse` using Pydantic v2. Import `date` from `datetime`. Change nothing
else. Invalid date strings must be rejected by Pydantic (422)."
Returned exactly the three field additions and the import. **Accepted.**

### Prompt 1.2
"Add `is_overdue(task, today=None)` to `app/storage.py`: return True only if the
task has a due date, `due_date < today`, and status is not Done. Add an optional
`overdue` filter to `get_all_tasks` that uses it. Do not store overdue on the task."
Returned the helper and filter. **Edited** to default `today = date.today()` when
not passed, so tests can inject a fixed date if needed. **Accepted** after that.

### Prompt 1.3
"Add pytest tests: valid due date returns 201, invalid format returns 422,
update due date returns 200, and an overdue filter that returns only overdue
tasks - include a past-due **Done** task that must be excluded."
Returned four tests. **Edited** the overdue test to build dates from
`date.today() ± timedelta` so it is deterministic. **Accepted.**

## Feature 2 - Search + combined filters

### Prompt 2.1
"Extend `GET /tasks` and `storage.get_all_tasks` with optional `search`
(case-insensitive substring of title OR description) and `assignee`
(case-insensitive exact), combined with the existing status/priority using AND.
An empty result stays 200 with []."
The assistant first suggested filtering in the frontend JavaScript. **Rejected**
that suggestion and kept the filtering in the backend via query params so it is
testable. **Accepted** the backend version.

### Prompt 2.2
"Add a compact filter bar above the board: a search input, a priority select, an
'Overdue only' checkbox and a Clear button. On change, rebuild the query string
and re-fetch. Keep all three columns visible with empty placeholders. Do not
change the drag-and-drop or the modal."
Returned the bar and wiring. **Edited** to debounce the search input (250 ms) so
it does not fire a request on every keystroke. **Accepted.**

### Prompt 2.3
"Add pytest tests: search matches both title and description, combined
status+priority returns the intersection, no match returns 200 with [], and an
invalid status filter value returns 422."
Returned four tests. **Accepted** as written after confirming each one passed and
then failed under a break test.
