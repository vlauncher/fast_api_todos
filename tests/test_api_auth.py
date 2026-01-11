import pytest
from fastapi.testclient import TestClient

def test_register_success(client):
    response = client.post(
        "/api/v1/register",
        json={
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["first_name"] == "New"
    assert data["last_name"] == "User"
    assert data["is_active"] is True
    assert data["is_verified"] is False
    assert "id" in data

def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/api/v1/register",
        json={
            "email": test_user.email,
            "first_name": "Duplicate",
            "last_name": "User",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_success(client, test_user):
    response = client.post(
        "/api/v1/login",
        json={"email": test_user.email, "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/v1/login",
        json={"email": test_user.email, "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_wrong_email(client):
    response = client.post(
        "/api/v1/login",
        json={"email": "nonexistent@example.com", "password": "password"}
    )
    assert response.status_code == 401

def test_login_unverified_user(db, client):
    from app.models import User
    from app.core.security import get_password_hash, generate_otp
    import datetime
    
    user = User(
        email="unverified@example.com",
        hashed_password=get_password_hash("testpass123"),
        first_name="Unverified",
        last_name="User",
        otp_code=generate_otp(),
        otp_created_at=datetime.datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    response = client.post(
        "/api/v1/login",
        json={"email": user.email, "password": "testpass123"}
    )
    assert response.status_code == 403
    assert "Account not verified" in response.json()["detail"]

def test_refresh_token_success(client, test_user):
    from app.core.security import create_refresh_token
    
    refresh_token = create_refresh_token(data={"sub": test_user.email})
    response = client.post(
        "/api/v1/refresh",
        json={"token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_refresh_token_invalid(client):
    response = client.post(
        "/api/v1/refresh",
        json={"token": "invalid_token"}
    )
    assert response.status_code == 401

def test_change_password_success(client, test_user, auth_headers):
    response = client.post(
        "/api/v1/change-password",
        json={"old_password": "testpass123", "new_password": "newpassword123"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "Password changed successfully" in response.json()["message"]

def test_change_password_wrong_old_password(client, test_user, auth_headers):
    response = client.post(
        "/api/v1/change-password",
        json={"old_password": "wrongpassword", "new_password": "newpassword123"},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Incorrect old password" in response.json()["detail"]

def test_change_password_unauthorized(client):
    response = client.post(
        "/api/v1/change-password",
        json={"old_password": "oldpass", "new_password": "newpass"}
    )
    assert response.status_code == 401

def test_forgot_password_existing_user(client, test_user):
    response = client.post(
        "/api/v1/forgot-password",
        json={"email": test_user.email}
    )
    assert response.status_code == 200
    assert "OTP has been sent" in response.json()["message"]

def test_forgot_password_nonexistent_user(client):
    response = client.post(
        "/api/v1/forgot-password",
        json={"email": "nonexistent@example.com"}
    )
    assert response.status_code == 200
    assert "OTP has been sent" in response.json()["message"]

def test_reset_password_success(db, client, test_user):
    from app.core.security import generate_otp
    import datetime
    
    otp = generate_otp()
    test_user.otp_code = otp
    test_user.otp_created_at = datetime.datetime.utcnow()
    db.commit()
    
    response = client.post(
        "/api/v1/reset-password",
        json={
            "email": test_user.email,
            "otp": otp,
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 200
    assert "Password reset successfully" in response.json()["message"]

def test_reset_password_invalid_otp(client, test_user):
    response = client.post(
        "/api/v1/reset-password",
        json={
            "email": test_user.email,
            "otp": "000000",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 400
    assert "Invalid OTP" in response.json()["detail"]
