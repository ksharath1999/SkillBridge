import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


# ---------------- HELPERS ----------------

def signup_user(name, email, password, role, institution_id=None):
    return client.post("/auth/signup", json={
        "name": name,
        "email": email,
        "password": password,
        "role": role,
        "institution_id": institution_id
    })


def login_user(email, password):
    return client.post("/auth/login", json={
        "email": email,
        "password": password
    })


# ---------------- TEST 1 ----------------
def test_signup_and_login():
    signup = signup_user(
        "Test Student",
        "teststudent@test.com",
        "1234",
        "student",
        1
    )

    # allow duplicate user case
    assert signup.status_code in [200, 400]

    login = login_user("teststudent@test.com", "1234")
    assert login.status_code == 200
    assert "access_token" in login.json()


# ---------------- TEST 2 ----------------
def test_trainer_create_session():
    login = login_user("trainer0@test.com", "1234")
    token = login.json()["access_token"]

    res = client.post(
        "/sessions",
        params={"batch_id": 1, "title": "Test Session"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code in [200, 201]
    assert "id" in res.json()


# ---------------- TEST 3 ----------------
def test_student_mark_attendance():
    login = login_user("student0@test.com", "1234")
    token = login.json()["access_token"]

    res = client.post(
        "/attendance/mark",
        params={"session_id": 1, "status": "present"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code in [200, 400]

    data = res.json()

    if res.status_code == 200:
        assert data["message"] == "Attendance marked"
    else:
        # FastAPI returns "detail" for HTTPException
        assert "detail" in data


# ---------------- TEST 4 ----------------
def test_monitoring_post_not_allowed():
    res = client.post("/monitoring/attendance")
    assert res.status_code == 405


# ---------------- TEST 5 ----------------
def test_no_token_protected():
    res = client.post("/batches", params={"name": "Test"})
    assert res.status_code == 401