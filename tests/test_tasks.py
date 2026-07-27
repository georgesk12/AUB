"""API tests for the Task Tracker (Module 2.4, prompt D1).

Every test is named after the behavior it protects. The Break Test (D3)
deliberately breaks production code to confirm the relevant tests fail -
a test you have never watched fail is decoration, not protection.
"""

# --------------------------------------------------------------------------
# POST /tasks
# --------------------------------------------------------------------------


def test_create_task_valid_returns_201_with_full_body(client):
    r = client.post(
        "/tasks",
        json={"title": "Write report", "priority": "High", "assignee": "georges"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Write report"
    assert body["priority"] == "High"
    assert body["assignee"] == "georges"
    assert body["status"] == "ToDo"          # default
    assert body["description"] == ""          # default
    assert body["id"]                         # server-generated id present
    assert body["created_at"] and body["updated_at"]


def test_create_task_missing_title_returns_422(client):
    r = client.post("/tasks", json={})
    assert r.status_code == 422


def test_create_task_blank_title_returns_422(client):
    r = client.post("/tasks", json={"title": "   "})
    assert r.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    r = client.post("/tasks", json={"title": "x", "priority": "Bogus"})
    assert r.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    r = client.post("/tasks", json={"title": "x", "made_up": "value"})
    assert r.status_code == 422


# --------------------------------------------------------------------------
# GET /tasks
# --------------------------------------------------------------------------


def test_list_tasks_empty_returns_200_and_empty_list(client):
    r = client.get("/tasks")
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(
    client, created_task
):
    # created_task is ToDo; filtering by Done should match nothing.
    r = client.get("/tasks", params={"status": "Done"})
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "high one", "priority": "High"})
    client.post("/tasks", json={"title": "low one", "priority": "Low"})
    r = client.get("/tasks", params={"priority": "High"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["priority"] == "High"


# --------------------------------------------------------------------------
# GET /tasks/{task_id}
# --------------------------------------------------------------------------


def test_get_task_by_id_returns_task(client, created_task):
    r = client.get(f"/tasks/{created_task['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created_task["id"]


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    r = client.get("/tasks/does-not-exist")
    assert r.status_code == 404
    assert "detail" in r.json()


# --------------------------------------------------------------------------
# PATCH /tasks/{task_id}
# --------------------------------------------------------------------------


def test_patch_partial_update_keeps_other_fields(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"title": "renamed"})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "renamed"
    assert body["status"] == created_task["status"]      # unchanged
    assert body["priority"] == created_task["priority"]  # unchanged


def test_patch_not_found_returns_404(client):
    r = client.patch("/tasks/does-not-exist", json={"title": "x"})
    assert r.status_code == 404


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    # created_task starts in ToDo; ToDo -> InProgress is allowed.
    r = client.patch(f"/tasks/{created_task['id']}", json={"status": "InProgress"})
    assert r.status_code == 200
    assert r.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    # ToDo -> Done skips InProgress and must be rejected.
    r = client.patch(f"/tasks/{created_task['id']}", json={"status": "Done"})
    assert r.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    # ToDo -> ToDo (same -> same) is not an allowed transition.
    r = client.patch(f"/tasks/{created_task['id']}", json={"status": "ToDo"})
    assert r.status_code == 422


# --------------------------------------------------------------------------
# DELETE /tasks/{task_id}
# --------------------------------------------------------------------------


def test_delete_existing_returns_204_no_body(client, created_task):
    r = client.delete(f"/tasks/{created_task['id']}")
    assert r.status_code == 204
    assert r.content == b""      # 204 must have an empty body


def test_delete_missing_returns_404(client):
    r = client.delete("/tasks/does-not-exist")
    assert r.status_code == 404


# --------------------------------------------------------------------------
# Expanded PATCH edge cases (Module 3.5). The frontend leans on PATCH for
# every drag move and every status edit, so these guard the rules that keep
# the board from accepting bad moves.
# --------------------------------------------------------------------------


def test_patch_backward_transition_inprogress_to_todo_returns_422(client, created_task):
    """A backward move (InProgress -> ToDo) must be rejected."""
    tid = created_task["id"]
    assert client.patch(f"/tasks/{tid}", json={"status": "InProgress"}).status_code == 200
    r = client.patch(f"/tasks/{tid}", json={"status": "ToDo"})
    assert r.status_code == 422


def test_patch_reopen_done_to_inprogress_returns_200(client, created_task):
    """Reopening a finished task (Done -> InProgress) is allowed."""
    tid = created_task["id"]
    client.patch(f"/tasks/{tid}", json={"status": "InProgress"})
    client.patch(f"/tasks/{tid}", json={"status": "Done"})
    r = client.patch(f"/tasks/{tid}", json={"status": "InProgress"})
    assert r.status_code == 200
    assert r.json()["status"] == "InProgress"


def test_patch_unsupported_status_value_returns_422(client, created_task):
    """An unknown status string (e.g. 'Archived') is rejected by the enum."""
    r = client.patch(f"/tasks/{created_task['id']}", json={"status": "Archived"})
    assert r.status_code == 422


def test_patch_priority_only_keeps_status_and_returns_200(client, created_task):
    """A priority-only edit must NOT trigger transition validation."""
    tid = created_task["id"]
    r = client.patch(f"/tasks/{tid}", json={"priority": "High"})
    assert r.status_code == 200
    body = r.json()
    assert body["priority"] == "High"
    assert body["status"] == "ToDo"   # status left untouched
