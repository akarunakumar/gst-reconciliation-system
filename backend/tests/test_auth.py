import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_success_admin():
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "admin"
    assert data["role"] == "admin"


def test_login_success_auditor():
    response = client.post("/api/v1/auth/login", json={"username": "auditor", "password": "Audit@123"})
    assert response.status_code == 200
    assert response.json()["role"] == "auditor"


def test_login_wrong_password():
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrongpass"})
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


def test_login_unknown_user():
    response = client.post("/api/v1/auth/login", json={"username": "ghost", "password": "anything"})
    assert response.status_code == 401


def test_logout():
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"


def test_refresh_token():
    login_resp = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@123"})
    refresh_token = login_resp.json()["refresh_token"]

    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data
    assert data["username"] == "admin"


def test_refresh_invalid_token():
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-valid-token"})
    assert response.status_code == 401


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
