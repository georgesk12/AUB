# Personal AI Usage Rules - Module 5.3

These are the working rules for using AI on this repo. They are written for a
developer, not for a legal department.

## My Rules

1. **I keep sensitive data out of the chat.**
   I do not paste credentials, tokens, `.env` contents, customer records,
   personal emails, production logs, private tickets, or anything that would be
   painful to see in a prompt history.

2. **I give AI the smallest useful context.**
   I share the files, transcript excerpt, or command output needed for the task,
   not an entire folder just because it is nearby.

3. **I name constraints before implementation.**
   In this repo: FastAPI, Pydantic v2, process-local memory storage, vanilla JS,
   no auth, no database, no ORM, exact status and priority enum values, and exact
   status-transition rules.

4. **I do not accept broad rewrites by default.**
   Small scoped changes are easier to review. If a generated change touches many
   files, I pause and ask whether the scope is justified.

5. **I verify behavior in the right layer.**
   Backend behavior gets pytest and API checks. Frontend behavior gets browser
   checks. Docs get checked against the code they describe.

6. **I distrust tests until they prove they can fail.**
   For rules that matter, I use break tests or targeted negative cases. Passing
   tests are not evidence if they cannot catch the intended regression.

7. **I classify AI review output before acting.**
   Review comments are sorted into useful, noise, wrong, valid, false positive,
   or course-scope risk. I do not accept a comment because it sounds senior.

8. **I keep a decision trail.**
   Prompts, rejected ideas, accepted changes, review conclusions, and security
   decisions belong in `docs/` when they affect the project direction.

9. **I do not let AI upgrade the assignment into a different product.**
   Authentication, persistence, frontend frameworks, background workers, and
   external services are out of scope unless the assignment or user explicitly
   asks for them.

10. **I treat production differently from learning work.**
    This course repo can be intentionally simple. Real software needs tighter
    rules for data handling, auth, dependency pinning, deployment, and audit
    trails.

## 30-Day Reminder

The useful habit is not "ask AI more." It is: ask with constraints, inspect the
diff, verify the behavior, and write down the decision when it matters.

The danger is not that AI is useless. The danger is that plausible output feels
finished before it has earned trust.

