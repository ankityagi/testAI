#!/usr/bin/env python3
"""Integration check for subtopic-aware question selection."""
from __future__ import annotations

import os
import sys
import time
from typing import Any

import requests

BASE_URL = os.getenv("STUDYBUDDY_BASE_URL", "http://localhost:8000")


def _url(path: str) -> str:
    return f"{BASE_URL.rstrip('/')}{path}"


def _print_step(message: str) -> None:
    print(message, flush=True)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _request(method: str, path: str, *, headers: dict[str, str] | None = None, json: Any | None = None) -> requests.Response:
    response = requests.request(method, _url(path), headers=headers, json=json, timeout=15)
    response.raise_for_status()
    return response


def main() -> None:
    timestamp = int(time.time())
    email = f"subtopic_tester_{timestamp}@example.com"
    password = "testpass123"

    _print_step("=== Phase 2 Subtopic Flow Integration Test ===\n")

    # 1. Sign up a fresh parent account
    _print_step("[1] Registering test parent account...")
    signup_resp = _request("POST", "/auth/signup", json={"email": email, "password": password})
    data = signup_resp.json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    _assert(token, "Signup response missing access token")
    _print_step("    ✓ Parent registered")

    # 2. Create a child profile (Grade 1 uses seeded math subtopics)
    _print_step("[2] Creating child profile...")
    child_resp = _request("POST", "/children/", headers=headers, json={"name": "Integration Child", "grade": 1})
    child = child_resp.json()
    child_id = child["id"]
    _assert(child_id, "Child creation response missing id")
    _print_step(f"    ✓ Child created: {child_id}")

    # 3. Fetch questions without specifying a subtopic (auto-selection path)
    _print_step("[3] Requesting questions without subtopic...")
    fetch_payload = {
        "child_id": child_id,
        "subject": "math",
        "topic": "addition",
        "limit": 5,
    }
    fetch_resp = _request("POST", "/questions/fetch", headers=headers, json=fetch_payload)
    batch = fetch_resp.json()

    auto_selected = batch.get("selected_subtopic")
    questions = batch.get("questions", [])

    _assert(auto_selected, "Auto-selection did not return a subtopic")
    _assert(questions, "Auto-selection returned no questions")
    for item in questions:
        _assert(item.get("sub_topic") == auto_selected, "Question sub_topic mismatch with auto-selected value")
    _print_step(f"    ✓ Auto-selected subtopic: {auto_selected}")
    _print_step(f"    ✓ Received {len(questions)} questions")

    # 4. Fetch questions with an explicit subtopic (user-specified path)
    _print_step("[4] Requesting questions with explicit subtopic...")
    explicit_resp = _request(
        "POST",
        "/questions/fetch",
        headers=headers,
        json={**fetch_payload, "subtopic": auto_selected},
    )
    explicit_batch = explicit_resp.json()
    _assert(explicit_batch.get("selected_subtopic") == auto_selected, "Explicit subtopic was not respected in response")
    _print_step("    ✓ Explicit subtopic honored")

    _print_step("\n=== ✓ Subtopic flow verified ===")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"\n✗ Integration test failed: {exc}")
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"\n✗ HTTP request failed: {exc}")
        sys.exit(1)
