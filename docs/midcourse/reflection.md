# Reflection - Mid-Course Feature Sprint

For this sprint I worked with Claude (Cowork) as a file-aware coding assistant.
Unlike the browser chat I used in Module 1, which could only see what I pasted
in, this assistant read and edited the real project files and ran the
verifications with me. I used it for three things: drafting small, scoped
changes (a model field, a storage helper, a filter bar), generating pytest
cases from a described scenario, and running the app and the suite to check each
layer before moving on. I kept the same discipline the course teaches - strict
prompts naming exact files and behavior, inspect before accepting, and verify
with tests, curl, the browser, and deliberate break tests.

One moment the AI clearly helped was building the search and filter layer. Once
I specified the exact query parameters and the AND-combining rule, it produced
the backend filter, the query-string builder, and a compact filter bar quickly
and consistently, including wiring each control to re-fetch. That is repetitive,
easy-to-get-slightly-wrong plumbing, and having it drafted let me spend my
attention on whether the behavior was correct rather than on typing.

One moment it slowed me down was my first, vague attempt at due dates. Asking it
to "add due dates" produced a broad change that touched several files at once
and guessed a date-time with a time component I did not want. Reviewing and
unwinding that took longer than if I had scoped it from the start. Rewriting the
prompt to name the exact field, type, and files fixed it immediately - a good
reminder that a weak prompt is not faster, it just moves the cost to review.

The place my review changed the result was the definition of "overdue." The
assistant's implementation treated any task past its due date as overdue,
including completed ones. That is subtly wrong: a finished task is not something
you still need to chase. I changed the rule so overdue requires the task to be
past due **and not Done**, and then wrote a test that seeds a past-due Done task
and asserts it is excluded. The break test confirmed the test actually catches
the mistake - when I removed the "not Done" condition, the test failed with
`assert 2 == 1`, and restoring it turned the suite green again.

The through-line is the same one from earlier modules: the assistant drafts
quickly and usefully, but it does not own the decisions or the correctness. I
do, because I defined the rules, reviewed every change, and verified the
behavior before trusting it.
