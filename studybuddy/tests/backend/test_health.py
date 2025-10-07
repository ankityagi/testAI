import os

from fastapi.testclient import TestClient

from studybuddy.backend import deps
from studybuddy.backend.app import create_app


def create_client() -> TestClient:
    os.environ["STUDYBUDDY_DATA_MODE"] = "memory"
    os.environ["STUDYBUDDY_MOCK_AI"] = "1"
    deps.reset_repository_cache()
    app = create_app()
    return TestClient(app)


def test_health_endpoint_returns_ok():
    client = create_client()

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_signup_child_flow_and_progress_reporting():
    client = create_client()

    signup = client.post(
        "/auth/signup",
        json={"email": "parent@example.com", "password": "Secret123"},
    )
    assert signup.status_code == 201
    token = signup.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    child_resp = client.post(
        "/children",
        json={"name": "Alex", "grade": 1, "zip": "10001"},
        headers=headers,
    )
    assert child_resp.status_code == 201
    child_id = child_resp.json()["id"]

    update_resp = client.patch(
        f"/children/{child_id}",
        json={"name": "Alexis", "grade": 2},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Alexis"
    assert update_resp.json()["grade"] == 2

    questions = client.post(
        "/questions/fetch",
        json={"child_id": child_id, "subject": "math", "limit": 5},
        headers=headers,
    )
    assert questions.status_code == 200
    question_payload = questions.json()["questions"]
    assert len(question_payload) >= 1
    question = question_payload[0]

    attempt = client.post(
        "/attempts",
        json={
            "child_id": child_id,
            "question_id": question["id"],
            "selected": question["correct_answer"],
            "time_spent_ms": 1500,
        },
        headers=headers,
    )
    assert attempt.status_code == 201
    assert attempt.json()["correct"] is True

    # Previously answered correctly questions should not repeat
    follow_up = client.post(
        "/questions/fetch",
        json={"child_id": child_id, "subject": "math", "limit": 5},
        headers=headers,
    )
    assert follow_up.status_code == 200
    follow_up_questions = follow_up.json()["questions"]
    assert follow_up_questions
    assert follow_up_questions[0]["hash"] != question["hash"]

    progress = client.get(f"/progress/{child_id}", headers=headers)
    assert progress.status_code == 200
    payload = progress.json()
    assert payload["attempted"] == 1
    assert payload["correct"] == 1
    assert payload["current_streak"] == 1
    assert payload["accuracy"] == 1.0

    children = client.get("/children", headers=headers)
    assert children.status_code == 200
    assert len(children.json()) == 1

    standards = client.get("/standards", headers=headers)
    assert standards.status_code == 200
    assert len(standards.json()) >= 1

    extra_child = client.post(
        "/children",
        json={"name": "Sam", "grade": 3},
        headers=headers,
    )
    assert extra_child.status_code == 201
    extra_child_id = extra_child.json()["id"]

    delete_resp = client.delete(f"/children/{extra_child_id}", headers=headers)
    assert delete_resp.status_code == 204

    children_after_delete = client.get("/children", headers=headers)
    payload_children = children_after_delete.json()
    assert all(child["id"] != extra_child_id for child in payload_children)
