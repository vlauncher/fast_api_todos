import pytest
from fastapi.testclient import TestClient

def test_get_current_user(client, test_user, auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["first_name"] == test_user.first_name

def test_get_current_user_unauthorized(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401

def test_update_current_user(client, test_user, auth_headers):
    response = client.put(
        "/api/v1/users/me",
        json={
            "first_name": "Updated",
            "last_name": "Name"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"
    assert data["email"] == test_user.email

def test_update_current_user_password(client, test_user, auth_headers):
    response = client.put(
        "/api/v1/users/me",
        json={"password": "newpassword123"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id

def test_update_current_user_unauthorized(client):
    response = client.put(
        "/api/v1/users/me",
        json={"first_name": "Updated"}
    )
    assert response.status_code == 401
