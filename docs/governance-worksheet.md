# Governance Retrospective - Module 5.3

This worksheet records what was shared with AI tools, what was accepted back
from them, and what governance rules should follow. It is intentionally
practical: the point is not policy theater, but rules a developer can actually
follow on the next project.

## What Was Shared With AI

| Item | Examples from this repo | Risk level | Reason | Rule going forward |
|---|---|---:|---|---|
| Toy project source code | `app/`, `frontend/index.html`, tests, Dockerfile, CI, docs | Low | The project is a course exercise with no real customer data, production secrets, or private business logic. | OK to share when the repo is intentionally used for AI-assisted coding practice. |
| Course prompts and transcripts | Module 2, 3, and 5 pasted transcripts and handouts | Low to Medium | Course material is private learning material, but it does not contain credentials or user data. | Share only the portion needed for the exercise; do not upload unrelated course material casually. |
| Local file paths | `/Users/georges/Documents/task-tracker-api`, Dropbox course-material paths | Medium | Paths can reveal personal names and folder structure even when code is harmless. | Share paths only when needed for local tooling; avoid including them in public writeups. |
| Test outputs and command results | Pytest counts, warnings, git status, browser verification notes | Low | Outputs describe the toy app and local tooling state, not sensitive records. | OK to share, but review logs before posting them publicly. |
| `.env` existence | The review noted that `.env` exists but did not inspect or quote it | High if contents are pasted | Environment files often contain secrets, even when this repo only needs placeholders. | Never paste `.env` contents into AI tools. Discuss only whether the file is ignored or excluded. |
| GitHub remote metadata | Repository URL and pushed commit identifiers | Low to Medium | Public repo metadata is usually fine, but it ties work to an account. | OK for this course repo; avoid exposing private remote URLs or branch names from client work. |
| Design and product decisions | Status transitions, no-auth scope, in-memory storage constraint | Low | These are intentional course constraints, not sensitive strategy. | Share, but label them as constraints so AI does not "improve" them into a different app. |

## What Was Received From AI

| Output | Accepted? | Verification used | Governance lesson |
|---|---:|---|---|
| Pydantic task model and storage scaffold | Yes, after inspection | Import checks, API tests, field-by-field review | Generated foundations need strict prompts because mistakes spread into every route. |
| CRUD endpoints | Yes, after endpoint checks | Swagger/curl-style verification and pytest | One endpoint at a time is easier to review than a broad generated API rewrite. |
| Status-transition business rule | Yes, after correction/confirmation | Transition matrix tests and invalid-transition checks | AI can validate enum values but miss state-machine intent unless the rule is explicit. |
| API tests | Yes, after break tests | Deliberately breaking validation and transitions | Tests are only useful after proving they fail for the bug they claim to catch. |
| Kanban board and modal UI | Yes, after browser checks | Local backend/frontend run, drag/drop rejection checks, form validation checks | Browser behavior needs direct verification; plausible UI code is not enough. |
| Docker review comments | Partly | Manual triage into Useful / Noise / Wrong | AI review is helpful as a sweep, not as an approval authority. |
| Security review | Yes, as documentation | Manual file scan and finding classification | Security output must separate valid risks, false positives, and course-scope decisions. |
| AGENTS.md guidance | Yes | Repo inspection and pushed commit | Repo-level AI instructions reduce repeated context loss and keep future work scoped. |

## Generated Code Trace

The clearest governance checkpoint in this repo is the status-transition rule:

```python
if payload.status is not None:
    validate_status_transition(existing.status, payload.status)
```

- `payload.status is not None` means the transition check only runs when the
  caller is actually changing status.
- `existing.status` is the server's current state, not a value trusted from the
  request body.
- `payload.status` is the requested next state after Pydantic has already
  validated that it is one of the allowed enum values.
- `validate_status_transition(...)` checks the pair, not just the destination.
  That is why `ToDo -> Done` is rejected even though `Done` is a valid status.

This block was safe to accept only because the surrounding tests cover allowed
transitions, forbidden jumps, same-status updates, and backward moves.

## Governance Rules

1. **Never paste secrets or private personal data.**
   `.env`, tokens, credentials, customer names, emails, tickets, production logs,
   and private incident details stay out of AI tools.

2. **Classify context before sharing it.**
   Low-risk toy code is acceptable. Private-but-nonsensitive code needs a reason.
   Secrets, credentials, and PII are high risk and should not be shared.

3. **State project constraints before asking for changes.**
   For this repo, that means no database, no auth, no ORM, vanilla JS frontend,
   in-memory storage, and exact status-transition rules unless the user changes
   scope.

4. **Treat generated output as a draft.**
   AI can propose code, tests, docs, and review findings. Acceptance requires
   inspection and evidence.

5. **Use tests as evidence, not decoration.**
   For important behavior, run the test and perform a break test when practical.
   A test that still passes when the behavior is broken is not trusted.

6. **Record AI contributions in repo docs.**
   Use files like `docs/midcourse/prompt-log.md`, `docs/code-review-4.5.md`,
   `docs/security-review.md`, and this worksheet so the decision trail survives
   the chat window.

7. **Separate course scope from production readiness.**
   No auth and in-memory storage are acceptable here because this is a learning
   app. They would be blockers for real deployment.

## Open Governance Notes

- The repo can continue using AI tools freely for course docs and toy-project
  code.
- Any future work involving real users, private business logic, production
  infrastructure, or credentials needs a separate sharing decision first.
- AI review comments should keep using explicit categories: useful, noise,
  wrong, valid, false positive, or course-scope risk.

