from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_signup():
    res = client.post("/auth/signup", json={
        "name": "Test",
        "email": "test@test.com",
        "password": "1234",
        "role": "student"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login():
    res = client.post("/auth/login", json={
        "email": "test@test.com",
        "password": "1234"
    })
    assert res.status_code == 200


def test_no_token_protected():
    res = client.post("/batches", params={"name": "Test"})
    assert res.status_code in [401, 403]


def test_monitoring_wrong_method():
    res = client.post("/monitoring/attendance")
    assert res.status_code == 405


def test_root():
    res = client.get("/")
    assert res.status_code == 200