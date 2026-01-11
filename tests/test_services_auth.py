import pytest
from app.services.auth_service import (
    authenticate_user,
    create_tokens,
    verify_otp,
    regenerate_otp,
    change_password,
    reset_password
)

def test_authenticate_user_success(db, test_user):
    user = authenticate_user(db, email=test_user.email, password="testpass123")
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email

def test_authenticate_user_wrong_password(db, test_user):
    user = authenticate_user(db, email=test_user.email, password="wrongpassword")
    assert user is None

def test_authenticate_user_wrong_email(db):
    user = authenticate_user(db, email="nonexistent@example.com", password="password")
    assert user is None

def test_create_tokens(db, test_user):
    tokens = create_tokens(test_user)
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert tokens.token_type == "bearer"
    assert len(tokens.access_token) > 0
    assert len(tokens.refresh_token) > 0

def test_verify_otp_success(db):
    from app.models import User
    from app.core.security import get_password_hash, generate_otp
    import datetime
    
    otp = generate_otp()
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        first_name="Test",
        last_name="User",
        otp_code=otp,
        otp_created_at=datetime.datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    result = verify_otp(db, email=user.email, otp=otp)
    assert result is True
    
    db.refresh(user)
    assert user.is_verified is True
    assert user.otp_code is None

def test_verify_otp_wrong_code(db):
    from app.models import User
    from app.core.security import get_password_hash, generate_otp
    import datetime
    
    otp = generate_otp()
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        first_name="Test",
        last_name="User",
        otp_code=otp,
        otp_created_at=datetime.datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    result = verify_otp(db, email=user.email, otp="000000")
    assert result is False

def test_verify_otp_expired(db):
    from app.models import User
    from app.core.security import get_password_hash, generate_otp
    import datetime
    
    otp = generate_otp()
    expired_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        first_name="Test",
        last_name="User",
        otp_code=otp,
        otp_created_at=expired_time
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    result = verify_otp(db, email=user.email, otp=otp)
    assert result is False

def test_verify_otp_user_not_found(db):
    result = verify_otp(db, email="nonexistent@example.com", otp="123456")
    assert result is False

def test_regenerate_otp(db, test_user):
    old_otp = test_user.otp_code
    new_otp = regenerate_otp(db, email=test_user.email)
    
    assert new_otp is not None
    assert len(new_otp) == 6
    assert new_otp != old_otp
    
    db.refresh(test_user)
    assert test_user.otp_code == new_otp

def test_regenerate_otp_user_not_found(db):
    with pytest.raises(ValueError, match="User not found"):
        regenerate_otp(db, email="nonexistent@example.com")

def test_change_password_success(db, test_user):
    from app.core.security import verify_password
    
    old_hashed = test_user.hashed_password
    change_password(db, test_user, "testpass123", "newpassword123")
    
    db.refresh(test_user)
    assert test_user.hashed_password != old_hashed
    assert verify_password("newpassword123", test_user.hashed_password) is True
    assert verify_password("testpass123", test_user.hashed_password) is False

def test_change_password_wrong_old_password(db, test_user):
    with pytest.raises(ValueError, match="Incorrect old password"):
        change_password(db, test_user, "wrongpassword", "newpassword123")

def test_reset_password_success(db):
    from app.models import User
    from app.core.security import get_password_hash, generate_otp, verify_password
    import datetime
    
    otp = generate_otp()
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("oldpassword"),
        first_name="Test",
        last_name="User",
        otp_code=otp,
        otp_created_at=datetime.datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    old_hashed = user.hashed_password
    reset_password(db, email=user.email, otp=otp, new_password="newpassword123")
    
    db.refresh(user)
    assert user.hashed_password != old_hashed
    assert user.otp_code is None
    assert verify_password("newpassword123", user.hashed_password) is True

def test_reset_password_wrong_otp(db):
    from app.models import User
    from app.core.security import get_password_hash, generate_otp
    import datetime
    
    otp = generate_otp()
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("oldpassword"),
        first_name="Test",
        last_name="User",
        otp_code=otp,
        otp_created_at=datetime.datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    with pytest.raises(ValueError, match="Invalid OTP"):
        reset_password(db, email=user.email, otp="000000", new_password="newpassword123")

def test_reset_password_expired_otp(db):
    from app.models import User
    from app.core.security import get_password_hash, generate_otp
    import datetime
    
    otp = generate_otp()
    expired_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("oldpassword"),
        first_name="Test",
        last_name="User",
        otp_code=otp,
        otp_created_at=expired_time
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    with pytest.raises(ValueError, match="OTP expired"):
        reset_password(db, email=user.email, otp=otp, new_password="newpassword123")

def test_reset_password_user_not_found(db):
    with pytest.raises(ValueError, match="User not found"):
        reset_password(db, email="nonexistent@example.com", otp="123456", new_password="newpassword123")
