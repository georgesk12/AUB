# Task Tracker - Technical Design Note

> A design note records *why*, not *what*. The code already shows what exists;
> this note captures the reasoning behind the choices - the alternatives that
> were rejected, what each decision cost, and what is still uncertain - before
> that reasoning disappears. It is not a README and it is not marketing.

## How to read this note (and who wrote which part)

The **Decisions** below are drafted from the code as *raw material* - the facts
of what was chosen and the mechanical reasons. The three sections at the end -
**Tradeoffs**, **Open questions**, and the **Reflection** - are written by the
developer from scratch, because an AI can describe the design but cannot know
what its author regrets, would change, or deliberately left out. Those are the
sections that make this note worth keeping.

---

## Decisions

### 1. In-memory storage, no database

**Decision.** Tasks live in a single process-local Python dict (`app/storage.py`),
keyed by a server-generated UUID. Nothing is persisted; the store is empty on
every restart.

**Why.** This is a learning project focused on API design, business rules and the
delivery layer - not on data engineering. A dict keeps the surface area tiny and
makes tests trivial to isolate (`_reset()` between tests).

**Alternatives rejected.** SQLite (real persistence, zero server) and a
Postgres + SQLAlchemy stack. Both were declined as out of scope in `CLAUDE.md` -
they would add schema, migrations and an ORM without teaching anything the API
work needs.

**Factual cost.** Data is lost on restart, and the design is single-process only
(see the Docker decision - this is why the container runs one worker).

### 2. Status transitions as an allow-list, not free assignment

**Decision.** A status change is legal only if the `(current, new)` pair is in a
`frozenset` `VALID_TRANSITIONS`: `ToDo -> InProgress`, `InProgress -> Done`,
`Done -> InProgress` (reopen). Everything else - including `ToDo -> Done`,
`Done -> ToDo`, and same -> same - is rejected with 422.

**Why.** The rule is about *which* moves are allowed, so it lives in data (a set
of pairs), not an if/elif chain. Adding or removing a legal move is a one-line
change, and same -> same is rejected implicitly by not being in the set.

**Alternatives rejected.** A free `status` setter (any value to any value) and a
hand-written conditional ladder. The setter has no business rule at all; the
ladder buries the rule in control flow and is harder to extend and test.

**Factual cost.** The allowed moves are hard-coded in source - changing a
workflow means a code change and a redeploy, not configuration.

### 3. Overdue is computed, never stored

**Decision.** A task is overdue when its `due_date` is strictly before today
**and** its status is not `Done`. This is computed on read (`is_overdue()`),
never written to the record.

**Why.** A stored flag would go stale the moment the clock crossed midnight or
the status changed. Computing it guarantees the answer always reflects the
current date and the latest status.

**Alternatives rejected.** A stored `is_overdue` boolean, or a nightly job that
recomputes flags. Both add a source of truth that can drift from reality.

**Factual cost.** Overdue cannot be filtered in a database query (there is no
database) - it is filtered in Python after loading the candidate tasks.

### 4. Strict input models (`extra="forbid"`)

**Decision.** Request models reject unknown fields, trim the title, require it to
be non-empty and cap it at 200 characters; status and priority are enum-checked.

**Why.** Fail loudly on malformed input at the edge, so bad data never reaches
the store. A typo'd field name is a 422, not a silently ignored value.

**Alternatives rejected.** Lenient models that ignore extra fields. Convenient,
but they hide client bugs and let unexpected data through.

### 5. CI: exact Python, plain pytest, on every push and PR

**Decision.** GitHub Actions runs one job on `ubuntu-latest`, pinned to Python
`3.14` (not `3.x`), caching pip, running bare `pytest` - no `continue-on-error`,
no `|| true`. It triggers on every push (any branch) and every pull request.

**Why.** CI must run a known interpreter so a green run means something, and the
test step must be allowed to fail the build - a pipeline that cannot turn red is
theater. This was proven with a deliberate red run and a green run.

**Alternatives rejected.** A version range/matrix (unnecessary for a single-target
learning project) and failure-swallowing flags (they defeat the purpose of CI).

### 6. Docker: multi-stage, non-root, pinned slim base

**Decision.** A multi-stage build installs dependencies into a venv in a builder
stage, then copies only that venv and `app/` into a `python:3.12-slim` runtime
that runs as a non-root `app` user, with a `HEALTHCHECK` polling `/health` and no
`--reload`.

**Why.** Multi-stage keeps build tooling out of the runtime image; non-root and a
minimal copy reduce attack surface; the healthcheck lets an orchestrator know the
container is actually serving. `3.12-slim` is pinned (not `latest`) for a known,
reproducible base.

**Deliberate inconsistency.** Local and CI run Python **3.14**, but the image runs
**3.12-slim** - chosen because 3.12-slim guarantees prebuilt arm64 wheels, so the
image builds without compiling from source. This is a known, accepted tradeoff,
documented here on purpose (see Open questions).

**Alternatives rejected.** A single-stage build (ships pip and build caches),
running as root (unnecessary privilege), and `python:latest` (unpinned, larger).

### 7. Frontend: one self-contained file, no build step

**Decision.** The entire Kanban UI is one `frontend/index.html` - vanilla HTML,
CSS and JS, no framework and no bundler. Drag is optimistic and reverts on a
rejected move.

**Why.** No build step means no toolchain to learn or break; the file opens and
runs. Optimistic drag keeps the UI responsive while the server stays the source
of truth.

**Alternatives rejected.** React/Vue + a bundler. Real benefits at scale, but for
one board they add a build system the project explicitly keeps out of scope.

---

## Tradeoffs - written from scratch by the developer

The one I am least comfortable with is the Python version split. I would have
preferred to run the image on the latest Python I have locally, which is 3.14. I
accepted 3.12-slim for the guaranteed arm64 wheels and a build that does not
compile from source, but that convenience is exactly what I traded against. My
worry is forward-looking: a dependency I add later may break on 3.12 while
working fine on my 3.14 local setup, and I would only find that out at build
time. So what I gave up on purpose is the confidence that local and production
run on identical footing - I took an easier build today in exchange for a gap I
will have to watch.

## Open questions - written from scratch by the developer

When persistence finally lands, the status allow-list should move into config
rather than stay hard-coded in the source. Workflows change, and changing which
transitions are legal should not mean a code change every time.

The overdue filter needs to be done the right way at that point too - pushed
into the database query itself, not filtered in Python after loading the
candidate tasks the way it works now. The open part is getting that query
correct against a real store rather than the in-memory dict.

## Reflection - one sentence, written from scratch

If I had known the full toolset from the start instead of having it introduced
module by module, I would have planned the development better and anticipated
the security and testing requirements earlier, rather than bolting them on as
each one came up.
