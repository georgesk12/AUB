# Debugging Log - Module 3.5

## Break-tests for the new PATCH edge-case tests

Every generated test was proven to **fail** when the behavior it protects is
broken, then the source was restored to green. A test that has never failed is
not trusted.

| Test | Break introduced in source | Result |
|------|----------------------------|--------|
| `test_patch_backward_transition_inprogress_to_todo_returns_422` | Added `(InProgress -> ToDo)` to `VALID_TRANSITIONS` | FAILED as expected |
| `test_patch_reopen_done_to_inprogress_returns_200` | Removed `(Done -> InProgress)` from `VALID_TRANSITIONS` | FAILED as expected |
| `test_patch_priority_only_keeps_status_and_returns_200` | Removed the `if payload.status is not None` guard in the PATCH route | FAILED as expected |
| `test_patch_unsupported_status_value_returns_422` | Enforced by the `TaskStatus` enum (Pydantic), not a business rule | n/a - type-level |

After each break the source was restored and `python -m pytest` returned
**22 passed**.

## Debugging session: the subtle "checks only the new status" bug

### 1. Bug introduced
In `app/business_rules.py`, `validate_status_transition` was changed from
checking the `(current, new)` pair to checking only the destination:

```python
# correct
if (current, new) not in VALID_TRANSITIONS:

# buggy
valid_targets = {t for _, t in VALID_TRANSITIONS}
if new not in valid_targets:   # only asks "is `new` a legal destination anywhere?"
```

This is the exact failure the module warns about: it *looks* like transition
validation but only asks "is `Done` a legal destination somewhere?" (yes)
instead of "is `ToDo -> Done` legal?" (no).

### 2. Evidence (real pytest output)

```
FAILURES
____________ test_patch_invalid_transition_todo_to_done_returns_422 ____________
    def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
        # ToDo -> Done skips InProgress and must be rejected.
        r = client.patch(f"/tasks/{created_task['id']}", json={"status": "Done"})
>       assert r.status_code == 422
E       assert 200 == 422
E        +  where 200 = <Response [200 OK]>.status_code
tests/test_tasks.py:125: AssertionError
FAILED tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422
1 failed, 4 passed
```

Only `ToDo -> Done` failed. Backward (`InProgress -> ToDo`) and same-to-same
still passed, because `ToDo` is not a valid destination of any transition -
which is precisely why a "check only the destination" bug is easy to miss in a
quick review.

### 3. Root cause
The rule is defined on the **pair** `(current, new)`, but the buggy check
discarded `current` and validated only `new`. Any status that is a legal
destination somewhere (`InProgress`, `Done`) would then be accepted from any
current state.

### 4. Fix
A cause fix, not a symptom fix - restored the pair check:

```python
if (current, new) not in VALID_TRANSITIONS:
```

No assertion was weakened and no `try/except` was added. The test was correct;
the source was wrong.

### 5. Confirmation
`python -m pytest` -> **22 passed**. The previously failing test passes again
with the corrected source.
