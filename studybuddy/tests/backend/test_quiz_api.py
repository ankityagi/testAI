"""API integration tests for quiz routes."""
import os
import time

from fastapi.testclient import TestClient

from studybuddy.backend import deps
from studybuddy.backend.app import create_app


def create_client() -> TestClient:
    """Create test client with memory mode."""
    os.environ["STUDYBUDDY_DATA_MODE"] = "memory"
    os.environ["STUDYBUDDY_MOCK_AI"] = "1"
    deps.reset_repository_cache()
    app = create_app()
    return TestClient(app)


def seed_test_questions():
    """Seed test questions directly into repository."""
    from studybuddy.backend import deps

    repo = deps.get_repository()

    # Create questions for testing
    questions = []
    for difficulty in ["easy", "medium", "hard"]:
        for i in range(20):
            questions.append({
                "subject": "math",
                "topic": "addition",
                "grade": 3,
                "difficulty": difficulty,
                "stem": f"{difficulty.capitalize()} question {i}: What is 2+2?",
                "options": ["2", "3", "4", "5"],
                "correct_answer": "4",
                "rationale": "2+2=4",
                "standard_ref": "3.OA.A.1",
            })

    # Insert directly into repository
    repo.insert_questions(questions)


def setup_authenticated_client():
    """Setup client with authenticated parent and child."""
    client = create_client()

    # Create parent account
    signup = client.post(
        "/auth/signup",
        json={"email": "quiz_test@example.com", "password": "Test123"},
    )
    assert signup.status_code == 201
    token = signup.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create child
    child_resp = client.post(
        "/children/",
        json={"name": "Quiz Tester", "grade": 3, "zip": "10001"},
        headers=headers,
    )
    assert child_resp.status_code == 201
    child_id = child_resp.json()["id"]

    # Seed test questions
    seed_test_questions()

    return client, headers, child_id


class TestQuizCreation:
    """Test quiz session creation."""

    def test_create_quiz_success(self):
        """Test successful quiz creation returns session without answers."""
        client, headers, child_id = setup_authenticated_client()

        response = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 10,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 0.3, "medium": 0.5, "hard": 0.2}
            },
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert "questions" in data
        assert len(data["questions"]) == 10

        # Verify questions don't include answers
        for q in data["questions"]:
            assert "stem" in q
            assert "options" in q
            assert "correct_choice" not in q
            assert "explanation" not in q

    def test_create_quiz_requires_auth(self):
        """Test quiz creation requires authentication."""
        client = create_client()

        response = client.post(
            "/quiz/sessions",
            json={
                "child_id": "some-id",
                "subject": "math",
                "topic": "addition",
                "question_count": 10,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 0.3, "medium": 0.5, "hard": 0.2}
            },
        )

        assert response.status_code == 401

    def test_create_quiz_validates_question_count(self):
        """Test quiz creation validates question count range."""
        client, headers, child_id = setup_authenticated_client()

        # Too few questions
        response = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 2,  # Min is 5
                "duration_sec": 600,
                "difficulty_mix": {"easy": 1.0, "medium": 0, "hard": 0}
            },
            headers=headers,
        )
        assert response.status_code == 422

        # Too many questions
        response = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 50,  # Max is 30
                "duration_sec": 600,
                "difficulty_mix": {"easy": 1.0, "medium": 0, "hard": 0}
            },
            headers=headers,
        )
        assert response.status_code == 422

    def test_create_quiz_validates_duration(self):
        """Test quiz creation validates duration range."""
        client, headers, child_id = setup_authenticated_client()

        # Too short
        response = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 10,
                "duration_sec": 100,  # Min is 300
                "difficulty_mix": {"easy": 1.0, "medium": 0, "hard": 0}
            },
            headers=headers,
        )
        assert response.status_code == 422

    def test_create_quiz_conflict_with_active_session(self):
        """Test cannot create duplicate active quiz for same subject/topic."""
        client, headers, child_id = setup_authenticated_client()

        # Create first quiz
        response1 = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 10,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 0.3, "medium": 0.5, "hard": 0.2}
            },
            headers=headers,
        )
        assert response1.status_code == 201

        # Try to create another active quiz for same subject/topic
        response2 = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 10,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 0.3, "medium": 0.5, "hard": 0.2}
            },
            headers=headers,
        )
        assert response2.status_code == 409
        assert "active_session_id" in response2.json()


class TestQuizRetrieval:
    """Test quiz session retrieval."""

    def test_get_quiz_session(self):
        """Test retrieving a quiz session."""
        client, headers, child_id = setup_authenticated_client()

        # Create quiz
        create_resp = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 10,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 0.3, "medium": 0.5, "hard": 0.2}
            },
            headers=headers,
        )
        session_id = create_resp.json()["session_id"]

        # Retrieve session
        response = client.get(f"/quiz/sessions/{session_id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["status"] == "active"
        assert data["subject"] == "math"
        assert data["topic"] == "addition"
        assert "questions" in data
        assert len(data["questions"]) == 10

    def test_get_quiz_session_requires_auth(self):
        """Test quiz retrieval requires authentication."""
        client = create_client()

        response = client.get("/quiz/sessions/fake-id")
        assert response.status_code == 401

    def test_list_quiz_sessions(self):
        """Test listing quiz sessions for a child."""
        client, headers, child_id = setup_authenticated_client()

        # Create multiple quizzes
        for i in range(3):
            client.post(
                "/quiz/sessions",
                json={
                    "child_id": child_id,
                    "subject": "math",
                    "topic": f"topic_{i}",
                    "question_count": 10,
                    "duration_sec": 600,
                    "difficulty_mix": {"easy": 0.3, "medium": 0.5, "hard": 0.2}
                },
                headers=headers,
            )

        # List sessions
        response = client.get("/quiz/sessions", headers=headers, params={"child_id": child_id})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Should be ordered by started_at descending
        assert all("id" in session for session in data)
        assert all("status" in session for session in data)


class TestQuizSubmission:
    """Test quiz submission and grading."""

    def test_submit_quiz_success(self):
        """Test successful quiz submission with grading."""
        client, headers, child_id = setup_authenticated_client()

        # Create quiz
        create_resp = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 10,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 0.3, "medium": 0.5, "hard": 0.2}
            },
            headers=headers,
        )
        data = create_resp.json()
        session_id = data["session_id"]
        questions = data["questions"]

        # Submit answers (answer first 5 correctly, rest incorrectly)
        answers = []
        for i, q in enumerate(questions):
            # Get correct answer by looking at options (first option for simplicity in test)
            selected = q["options"][0] if i < 5 else "wrong_answer"
            answers.append({
                "question_id": q["question_id"],
                "selected_choice": selected
            })

        # Wait a moment so time_taken > 0
        time.sleep(0.1)

        submit_resp = client.post(
            f"/quiz/sessions/{session_id}/submit",
            json={"answers": answers},
            headers=headers,
        )

        assert submit_resp.status_code == 200
        result = submit_resp.json()
        assert "score" in result
        assert "correct_count" in result
        assert "total_questions" in result
        assert result["total_questions"] == 10
        assert "incorrect_items" in result
        assert "time_taken_sec" in result
        assert result["time_taken_sec"] > 0

    def test_submit_quiz_with_unanswered_questions(self):
        """Test submitting quiz with some unanswered questions."""
        client, headers, child_id = setup_authenticated_client()

        # Create quiz
        create_resp = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 10,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 1.0, "medium": 0, "hard": 0}
            },
            headers=headers,
        )
        session_id = create_resp.json()["session_id"]
        questions = create_resp.json()["questions"]

        # Only answer first 5 questions
        answers = [
            {"question_id": q["question_id"], "selected_choice": q["options"][0]}
            for q in questions[:5]
        ]

        submit_resp = client.post(
            f"/quiz/sessions/{session_id}/submit",
            json={"answers": answers},
            headers=headers,
        )

        assert submit_resp.status_code == 200
        result = submit_resp.json()
        assert result["unanswered_count"] == 5

    def test_submit_quiz_requires_auth(self):
        """Test quiz submission requires authentication."""
        client = create_client()

        response = client.post(
            "/quiz/sessions/fake-id/submit",
            json={"answers": []},
        )
        assert response.status_code == 401

    def test_submit_quiz_updates_status(self):
        """Test quiz status changes to completed after submission."""
        client, headers, child_id = setup_authenticated_client()

        # Create and submit quiz
        create_resp = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 5,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 1.0, "medium": 0, "hard": 0}
            },
            headers=headers,
        )
        session_id = create_resp.json()["session_id"]
        questions = create_resp.json()["questions"]

        # Submit answers
        answers = [
            {"question_id": q["question_id"], "selected_choice": q["options"][0]}
            for q in questions
        ]
        client.post(
            f"/quiz/sessions/{session_id}/submit",
            json={"answers": answers},
            headers=headers,
        )

        # Check status changed
        get_resp = client.get(f"/quiz/sessions/{session_id}", headers=headers)
        assert get_resp.json()["status"] == "completed"

    def test_cannot_submit_same_quiz_twice(self):
        """Test idempotency - cannot submit same quiz twice."""
        client, headers, child_id = setup_authenticated_client()

        # Create quiz
        create_resp = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 5,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 1.0, "medium": 0, "hard": 0}
            },
            headers=headers,
        )
        session_id = create_resp.json()["session_id"]
        questions = create_resp.json()["questions"]

        # Submit first time
        answers = [
            {"question_id": q["question_id"], "selected_choice": q["options"][0]}
            for q in questions
        ]
        first_submit = client.post(
            f"/quiz/sessions/{session_id}/submit",
            json={"answers": answers},
            headers=headers,
        )
        assert first_submit.status_code == 200

        # Try to submit again
        second_submit = client.post(
            f"/quiz/sessions/{session_id}/submit",
            json={"answers": answers},
            headers=headers,
        )
        assert second_submit.status_code == 400  # Already submitted


class TestQuizExpiry:
    """Test quiz session expiry."""

    def test_expire_quiz_session(self):
        """Test manually expiring a quiz session."""
        client, headers, child_id = setup_authenticated_client()

        # Create quiz
        create_resp = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 5,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 1.0, "medium": 0, "hard": 0}
            },
            headers=headers,
        )
        session_id = create_resp.json()["session_id"]

        # Expire session
        expire_resp = client.post(
            f"/quiz/sessions/{session_id}/expire",
            headers=headers,
        )

        assert expire_resp.status_code == 200

        # Check status changed
        get_resp = client.get(f"/quiz/sessions/{session_id}", headers=headers)
        assert get_resp.json()["status"] == "expired"

    def test_cannot_submit_expired_quiz(self):
        """Test cannot submit answers to expired quiz."""
        client, headers, child_id = setup_authenticated_client()

        # Create and expire quiz
        create_resp = client.post(
            "/quiz/sessions",
            json={
                "child_id": child_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 5,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 1.0, "medium": 0, "hard": 0}
            },
            headers=headers,
        )
        session_id = create_resp.json()["session_id"]
        questions = create_resp.json()["questions"]

        # Expire it
        client.post(f"/quiz/sessions/{session_id}/expire", headers=headers)

        # Try to submit
        answers = [
            {"question_id": q["question_id"], "selected_choice": q["options"][0]}
            for q in questions
        ]
        submit_resp = client.post(
            f"/quiz/sessions/{session_id}/submit",
            json={"answers": answers},
            headers=headers,
        )

        assert submit_resp.status_code == 410  # Gone


class TestQuizSecurity:
    """Test quiz security and authorization."""

    def test_cannot_access_other_users_quiz(self):
        """Test users cannot access quizzes from other users."""
        client = create_client()

        # Create first user and quiz
        signup1 = client.post(
            "/auth/signup",
            json={"email": "user1@example.com", "password": "Test123"},
        )
        token1 = signup1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        child1_resp = client.post(
            "/children/",
            json={"name": "Child 1", "grade": 3},
            headers=headers1,
        )
        child1_id = child1_resp.json()["id"]

        create_resp = client.post(
            "/quiz/sessions",
            json={
                "child_id": child1_id,
                "subject": "math",
                "topic": "addition",
                "question_count": 5,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 1.0, "medium": 0, "hard": 0}
            },
            headers=headers1,
        )
        session_id = create_resp.json()["session_id"]

        # Create second user
        signup2 = client.post(
            "/auth/signup",
            json={"email": "user2@example.com", "password": "Test123"},
        )
        token2 = signup2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User 2 tries to access user 1's quiz
        response = client.get(f"/quiz/sessions/{session_id}", headers=headers2)
        assert response.status_code in [403, 404]  # Forbidden or Not Found

    def test_child_validation_on_quiz_creation(self):
        """Test quiz creation validates child belongs to parent."""
        client, headers, _ = setup_authenticated_client()

        # Try to create quiz with non-existent child
        response = client.post(
            "/quiz/sessions",
            json={
                "child_id": "fake-child-id",
                "subject": "math",
                "topic": "addition",
                "question_count": 10,
                "duration_sec": 600,
                "difficulty_mix": {"easy": 0.3, "medium": 0.5, "hard": 0.2}
            },
            headers=headers,
        )

        assert response.status_code in [400, 403, 404]
