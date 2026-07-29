# Final AI Review and Ownership Evidence

The main AI-assisted-coding evidence document for the final project. It shows how
AI output was reviewed, graded, corrected, or rejected across this repo - not
accepted blindly. Every row names a real file and a real decision.

## AGENTS.md guardrails

- **Repo-specific stack and commands included:** yes. `AGENTS.md` lists the
  FastAPI / Pydantic v2 / in-memory / vanilla-JS stack and the install, backend,
  frontend, test, and Docker commands under "Commands".
- **Docs-first / read-first guardrail included:** yes. "Module 5 Guardrails"
  says prefer read-only analysis first and put deliverables in `docs/` unless the
  user explicitly asks otherwise.
- **Unexpected app/frontend edits rule included:** yes. Same section: "Do not
  modify `app/`, `frontend/`, tests, CI, Docker, or dependencies during
  review/governance/planning tasks without explicit approval."

## AI code review mini-log

Source diff: commit `3cfd2bc` (the Dockerfile + `.dockerignore`), triaged in full
in `docs/code-review-4.5.md`. Grades repeated here with the verification.

| AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|
| "Add `--workers 4` for production throughput." | **Wrong** | Storage is a per-process in-memory dict. Multiple workers means separate stores, so a GET after a POST would randomly 404. | Rejected. Traced to `app/storage.py` (`_tasks` module-level dict) and the in-memory constraint in `AGENTS.md`/`CLAUDE.md`. Would break behavior if accepted. |
| "`requirements.txt` ships `pytest` and `httpx` into the runtime image." | **Useful** | The builder installs all of `requirements.txt` and the venv is copied to runtime, so the production image carries the test toolchain. | Confirmed: `requirements.txt` lists both under dev/testing. Logged as a real dep-hygiene backlog item (split runtime vs dev deps). |
| "The runtime stage never installs dependencies - it will crash with ModuleNotFoundError." | **Wrong** | Misreads the multi-stage build: `COPY --from=builder /opt/venv /opt/venv` plus `PATH=/opt/venv/bin` makes every dependency present. | Rejected. Already disproven empirically - the container built and served `/health` in Module 4.3. |
| "Pin the base image by `@sha256` digest." | **Noise** | True as general best practice but out of course scope; `CLAUDE.md`/`AGENTS.md` require an explicit minor (`3.12-slim`), which is met. | No action. Recorded as a production-only nicety. |

## AI security mini-review

Source: `docs/security-review.md` (Module 5.2 read-only review, graded and
reconciled with a manual scan). Representative findings:

| Finding | File evidence | Grade | Reason | Next action |
|---|---|---|---|---|
| No authentication protects task CRUD. | `app/main.py:18-26`; app description says "no authentication"; all routes public. | **Valid** | Intentional course-scope decision, but a real production blocker. | Keep for the course; add auth + ownership + tests before any real deployment. |
| `description` and `assignee` are unbounded strings in an in-memory store. | `app/models/__init__.py:53-58`, `app/storage.py:21-23`; only `title` is capped at 200. | **Valid** | Concrete oversized-payload / memory risk. Simple and testable to fix. | Backlog: add max lengths + 422 tests for overlong values. |
| Frontend is vulnerable to XSS. | `frontend/index.html`; fields rendered with `textContent`, not `innerHTML`. | **False Positive** | The risky pattern is absent; safe DOM text assignment is used throughout. | No action. Keep using `textContent` for user data. |
| Error details echo caller-supplied task IDs and status values. | `app/main.py:145-148, 180-183, 214-217`; `app/business_rules.py:41-46`. | **Noise** | Technically true, but IDs/statuses are not sensitive here and the messages aid usability. | No action; avoid putting secrets/paths in future error messages. |

## Manual security check

I ran my own scan after grading the AI output, without re-reading its answer.
Two things came out of it. First, a finding the AI review under-weighted: the
`search` and `assignee` **query** params (`app/main.py:92-127`) are also unbounded
and drive per-task work on every request - easier to miss than body-field limits
because the values are not stored directly. Second, I re-read `frontend/index.html`
end to end to confirm the XSS false positive myself: every user-controlled field
(title, description, assignee, due date, toast/error text) is written with
`textContent`. Finding nothing new there is itself a valid result - it confirms
the false-positive grade rather than taking the AI's word for it.

## One AI output I rejected or corrected

The clearest rejection is the "`--workers 4`" Docker suggestion above: it sounds
like standard production advice, but with a per-process in-memory store it would
make tasks appear and disappear depending on which worker answered. I did not
apply it. Separately, during Module 4.4 I corrected four stale documentation
claims that AI-generated docs had carried forward - most visibly the FastAPI
`description="Learning-project task tracker (Module 2)."`, which rendered live at
`/docs` on a Module-4 app; I rewrote it to describe the real API (logged in
`docs/documentation-verification.md`).

## Three AI usage rules

1. **Never paste** `.env` contents, credentials, tokens, production logs, or real
   customer/personal data into an AI tool. Only toy-project code and the minimum
   context the task needs.
2. **Always verify** against ground truth before accepting output - run the test
   (and break it on purpose for rules that matter), `curl` the endpoint, read the
   diff, check the claim against the actual file. A green check or a confident
   answer is not evidence.
3. **Record AI contributions** in repo docs so the decision trail outlives the
   chat window: `docs/code-review-4.5.md`, `docs/security-review.md`,
   `docs/governance-worksheet.md`, and this file.

## Ownership statement

I am comfortable submitting this repo as my own work. AI drafted and reviewed
parts of it, but I set the constraints, read every diff before it was applied,
and verified behavior in the right layer - pytest and `curl` for the backend,
the browser for the frontend, and the actual commit and container for CI and
Docker. I can explain every changed line, command, and config choice, including
why the storage is in-memory, why the status transitions are an allow-list, and
why I rejected the AI suggestions that would have broken those decisions. Where
AI was confidently wrong - the `--workers` suggestion, the stale doc claims, the
XSS false positive - I caught it and said why. The judgment in these documents is
mine, and the code stays inside the scope I chose.
