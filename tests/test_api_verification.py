import pytest
from fastapi.testclient import TestClient

def test_verify_otp_success(db, client):
    from app.models import User
    from app.core.security import get_password_hash, generate_otp
    import datetime
    
    otp = generate_otp()
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        first_name="Test",
        last_name="User",
        otp_code=otp,
        otp_created_at=datetime.datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    response = client.post(
        "/api/v1/verify-otp",
        json={"email": user.email, "otp": otp}
    )
    assert response.status_code == 200
    assert "Account verified successfully" in response.json()["message"]
    
    db.refresh(user)
    assert user.is_verified is True
    assert user.otp_code is None

def test_verify_otp_already_verified(client, test_user):
    response = client.post(
        "/api/v1/verify-otp",
        json={"email": test_user.email, "otp": "123456"}
    )
    assert response.status_code == 200
    assert "User already verified" in response.json()["message"]

def test_verify_otp_invalid_code(db, client):
    from app.models import User
    from app.core.security import get_password_hash, generate_otp
    import datetime
    
    otp = generate_otp()
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        first_name="Test",
        last_name="User",
        otp_code=otp,
        otp_created_at=datetime.datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    response = client.post(
        "/api/v1/verify-otp",
        json={"email": user.email, "otp": "000000"}
    )
    assert response.status_code == 400
    assert "Invalid or expired OTP" in response.json()["detail"]

def test_verify_otp_expired(db, client):
    from app.models import User
    from app.core.security import get_password_hash, generate_otp
    import datetime
    
    otp = generate_otp()
    expired_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        first_name="Test",
        last_name="User",
        otp_code=otp,
        otp_created_at=expired_time
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    response = client.post(
        "/api/v1/verify-otp",
        json={"email": user.email, "otp": otp}
    )
    assert response.status_code == 400
    assert "Invalid or expired OTP" in response.json()["detail"]

def test_verify_otp_user_not_found(client):
    response = client.post(
        "/api/v1/verify-otp",
        json={"email": "nonexistent@example.com", "otp": "123456"}
    )
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_resend_otp_success(db, client):
    from app.models import User
    from app.core.security import get_password_hash, generate_otp
    import datetime
    
    otp = generate_otp()
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        first_name="Test",
        last_name="User",
        otp_code=otp,
        otp_created_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    old_otp = user.otp_code
    response = client.post(
        "/api/v1/resend-otp",
        params={"email": user.email}
    )
    assert response.status_code == 200
    assert "OTP resent successfully" in response.json()["message"]
    
    db.refresh(user)
    assert user.otp_code != old_otp

def test_resend_otp_already_verified(client, test_user):
    response = client.post(
        "/api/v1/resend-otp",
        params={"email": test_user.email}
    )
    assert response.status_code == 200
    assert "User already verified" in response.json()["message"]

def test_resend_otp_user_not_found(client):
    response = client.post(
        "/api/v1/resend-otp",
        params={"email": "nonexistent@example.com"}
    )
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]
