# My Personal AI Coding Playbook

One page, my own workflow, revised after the final project. Every rule is here
because a specific thing went right or wrong while I built this task tracker -
not because it sounds responsible.

## When I reach for AI first

For a build-and-verify loop on a well-scoped task: I built the backend (M2), the
Kanban frontend (M3), and the mid-course features here. For read-and-grade work -
security review, code review, governance, and repo-grounded planning (M5). For
drafting structure I will then rewrite in my own voice - stories, ADRs, the
technical note. AI is fastest when I already know what "done" looks like and can
check the result.

## When I do not reach for AI first

When the task is one deliberate line I already understand. When I have not yet
decided what "done" means - an under-specified prompt just produces confident
noise. When I am about to paste anything sensitive. And when the point is for me
to learn the thing myself, not to have it handed over.

## My non-negotiables

1. **I verify against ground truth, not a convenient UI.** The CI "Re-run all
   jobs" button replayed an old commit and stayed green until I pushed a *new*
   commit and read *that* run; Chrome served cached pages from a dead server. I
   trust the commit, the `curl`, the `pytest` run, and the raw file.
2. **I grade AI review; I never accept it because it sounds senior.** Four of
   nine comments on an 84-line Docker diff were wrong, and "`--workers 4`" would
   have silently broken my in-memory store.
3. **I state my constraints before I ask.** In-memory storage, no auth, no
   database, vanilla JS, exact status and transition rules - or AI "improves" the
   assignment into a different product.
4. **I distrust a test until it has failed on purpose.** A passing test is not
   evidence until I have broken the behavior it guards and watched it go red.

## My review rules

I keep AI changes small and scoped so a diff is readable; a change that sprawls
across many files gets paused and questioned. I read every diff before it is
applied - Codex's diff-before-apply pane is the point, not a formality. I sort
every review comment into useful, noise, wrong, valid, false positive, or
course-scope, and each one needs a reason before I act. I run the command myself
rather than trusting the summary of it. And I never weaken a test to make the
suite pass.

## What I am still figuring out

Whether "review and plan in Codex, build and write in Cowork" holds once tasks
get bigger, or whether one tool eventually wins for me. How a team would agree on
these rules rather than each developer keeping a private playbook. Where the line
really sits between a smooth long-running agent thread and one that has quietly
changed too many files before I looked. And when the in-memory-vs-real-database
line finally forces local and production onto the same footing.

## Decision card

| Situation | Tool I reach for first | The reason |
|---|---|---|
| **New feature** | Claude (Cowork) | A build-and-verify loop in one place; it is how I built M2-M4. |
| **Code review** | Codex app | Review pane, diff-before-apply, higher limits - grading beats building here. |
| **Debugging** | Claude (Cowork) + terminal as truth | The "haunted Mac": the browser lied, `curl`/`lsof`/Firefox told the truth. |
| **Infrastructure (CI/Docker)** | Claude (Cowork), terminal delivery | Where CLAUDE.md, the red-and-green CI, and the non-root image came from. |
| **Never paste** | (no tool) | `.env`, secrets, tokens, production logs, real customer/personal data. |
| **One rule I will never break** | (every tool) | I sign every line - I do not ship AI output I have not read and verified myself: not a green check, not a confident answer, not a passing test I have not tried to break. |

## 30-day check

Reread this in a month and ask the uncomfortable question: am I still following
these rules, or did the rules quietly change because a smooth interface made
accepting output feel like progress? If a rule no longer fits how I work, rewrite
it honestly - do not keep it on the page for show.
