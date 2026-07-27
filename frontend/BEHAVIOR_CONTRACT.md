# Frontend Behavior Contract

The list of behaviors the Task Board must preserve. Run through it **before**
a refactor (to prove it passes) and **again after** (to prove the refactor
changed appearance/structure only, not behavior). If any item fails after a
refactor, fix that one section - do not accept a broad rewrite.

Backend running on `http://localhost:8000`, frontend served over HTTP (not
`file://`). Statuses are `ToDo` / `InProgress` / `Done`; priorities are
`High` / `Medium` / `Low`.

## Board rendering
- [ ] Three columns always render: **To Do**, **In Progress**, **Done**.
- [ ] Each column header shows a live **count** of its cards.
- [ ] Cards show title, a colored **priority badge**, and (when present)
      description and assignee.

## Priority sorting
- [ ] Within a column, cards are ordered **High → Medium → Low**.
- [ ] Ties break on a stable secondary key (task id), not alphabetically.

## UI states
- [ ] **Loading**: a loading indicator shows while `GET /tasks` is in flight.
- [ ] **Ready**: the board shows when data has loaded.
- [ ] **Empty**: a column with no tasks still renders with a "No tasks"
      placeholder (never a blank page).
- [ ] **Error**: if the backend is unreachable, an error banner with a
      **Retry** button shows instead of the board.

## Drag and drop
- [ ] A **valid** move (e.g. ToDo → InProgress) moves the card and sends
      `PATCH /tasks/{id}` returning **200**; the card stays.
- [ ] An **invalid** move (e.g. ToDo → Done, or Done → ToDo) is rejected with
      **422**; the card **reverts** to its original column and a message shows.
- [ ] Dropping a card back into its **own** column sends **no** PATCH request.
- [ ] The target status comes from the **column**, not the displayed label.

## Create (modal)
- [ ] The **+ New Task** button opens the modal in create mode.
- [ ] An empty / whitespace-only title is **blocked in the browser** with a
      field error and **no network request** is sent.
- [ ] A valid create sends `POST /tasks` and the board refreshes with the new
      card in the correct column and sorted position.

## Edit (modal)
- [ ] The **Edit** button on a card opens the modal pre-filled with its data.
- [ ] Editing only the priority sends `PATCH` and re-sorts the column; it does
      **not** resend an unchanged status (which would be rejected as a
      same→same transition).
- [ ] An edit that requests an **invalid transition** keeps the modal **open**
      and shows the server's error message (does not silently close).

## Dismissal
- [ ] **Cancel** closes the modal without saving.
- [ ] The **✕** close button closes the modal.
- [ ] **Escape** closes the modal.
- [ ] Clicking the dark **overlay** closes the modal.

---

### Refactor log
| Date | What was refactored | Contract passed before | Contract passed after |
|------|---------------------|------------------------|-----------------------|
| 2026-07 | CSS visual refresh (gradient, card/button polish); no HTML/JS logic changes | yes | yes |
| 2026-07 | Extract the frontend overdue rule into a named `isOverdue()` helper; behavior unchanged | yes | yes |
