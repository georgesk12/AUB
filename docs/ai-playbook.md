# My Personal AI Coding Playbook

One page. My own workflow, built from what actually happened across this course -
not a vendor page and not advice that would fit any other student. Every rule
below is here because a specific thing went right or wrong while I built this
task tracker.

## Decision card - which tool I reach for first

| Task shape | I reach for | Why - from my own experience |
|---|---|---|
| **Build a feature / larger implementation loop** | **Claude (Cowork)** | I built the whole backend (M2), the Kanban frontend (M3) and the mid-course features here, and I turned Cursor down on purpose. A build-and-verify loop in one place is how I actually work. |
| **Code review, security review, governance** | **Codex app** | I ran all of Module 5's grading work in Codex. Its review pane, diff-before-apply, and higher limits fit read-and-grade work better than a build loop does. |
| **Debugging** | **Claude (Cowork) + the terminal as ground truth** | Module 3.5 and the "haunted Mac": the browser showed my pages as up while the server was dead. `curl`, `lsof` and Firefox were the truth. I debug against ground truth, in a tool that can run it. |
| **Infrastructure - CI, Docker** | **Claude (Cowork), terminal delivery** | Module 4: CLAUDE.md, the red-and-green CI proof, and the non-root Docker image were all terminal-delivery work, and that is where that tool is strongest. |
| **Planning / architecture** | **Codex app, repo-grounded** | Module 5.4 and 5.5 showed me a generic plan reads fine and is still wrong for my project. A plan is only worth grading when the agent read my actual files first. |
| **Requirements and written docs** | **Claude (Cowork)** | Module 1 stories and ADR, the Word deliverables, and the technical note all came together fastest here, drafting structure then rewriting in my voice. |

The split I actually settled into: **build, deliver and write in Cowork; review,
govern and plan in Codex.** Cursor and Copilot I evaluated and set aside - not
because they cannot do the work, but because these two match how I want to work.

## When I do not reach for AI

When the task is one deliberate line I already understand, when I am about to
paste anything sensitive, or when I have not yet decided what "done" looks like.
AI is fast and confidently wrong often enough that pointing it at an
under-specified task just produces confident noise.

## My non-negotiables

1. **I verify against ground truth, never a convenient UI.**
   The CI "Re-run all jobs" button replayed an old commit and stayed green until
   I pushed a *new* commit and read *that* run. Chrome served cached pages from a
   dead server. So I trust the commit, the `curl`, the `pytest` run and the raw
   file - not the checkmark and not the confident answer.

2. **I grade AI review output; I never accept it because it sounds senior.**
   On an 84-line Docker diff, four of nine AI comments were wrong, and the
   worst - "add `--workers 4`" - would have silently broken my per-process
   in-memory store. Every finding gets a label: useful, noise, wrong, or
   course-scope - before it gets acted on.

3. **I state my constraints before I ask for anything.**
   In-memory storage, no auth, no database, vanilla-JS frontend, exact status and
   transition rules. Without those named up front, AI "improves" the assignment
   into a different product - workers, a DB, a framework I never asked for.

4. **I distrust a test until it has failed on purpose.**
   A passing test is not evidence until I have broken the behavior it guards and
   watched it go red, then restored it. That is how I proved the transition rules
   and the CI pipeline actually protect something.

## The one rule I will never break

**I sign every line. I do not ship AI output I have not read and verified myself -
not a green check, not a confident explanation, not a passing test I have not
tried to break.** The tool is a fast junior collaborator who is wrong about a
third of the time. Owning the result is my job, and it is the whole point of the
course.

## 30-day check

Reread this in a month and ask the uncomfortable question: am I still following
these rules, or did the rules quietly change because a smooth interface made
accepting output feel like progress? If a rule no longer fits how I work, rewrite
it honestly - do not just keep it on the page for show.
