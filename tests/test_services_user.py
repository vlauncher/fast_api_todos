import pytest
from app.schemas import UserCreate, UserUpdate
from app.services.user_service import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    update_user
)

def test_get_user_by_email(db, test_user):
    user = get_user_by_email(db, email=test_user.email)
    assert user is not None
    assert user.email == test_user.email
    assert user.id == test_user.id

def test_get_user_by_email_not_found(db):
    user = get_user_by_email(db, email="nonexistent@example.com")
    assert user is None

def test_get_user_by_id(db, test_user):
    user = get_user_by_id(db, user_id=test_user.id)
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email

def test_get_user_by_id_not_found(db):
    user = get_user_by_id(db, user_id=99999)
    assert user is None

def test_create_user(db):
    user_data = UserCreate(
        email="newuser@example.com",
        first_name="New",
        last_name="User",
        password="password123"
    )
    user = create_user(db, user_data)
    assert user.id is not None
    assert user.email == "newuser@example.com"
    assert user.first_name == "New"
    assert user.last_name == "User"
    assert user.is_active is True
    assert user.is_verified is False
    assert user.otp_code is not None
    assert len(user.otp_code) == 6

def test_create_user_duplicate_email(db, test_user):
    user_data = UserCreate(
        email=test_user.email,
        first_name="Duplicate",
        last_name="User",
        password="password123"
    )
    with pytest.raises(ValueError, match="Email already registered"):
        create_user(db, user_data)

def test_update_user(db, test_user):
    user_update = UserUpdate(
        first_name="Updated",
        last_name="Name"
    )
    updated_user = update_user(db, test_user, user_update)
    assert updated_user.first_name == "Updated"
    assert updated_user.last_name == "Name"
    assert updated_user.email == test_user.email

def test_update_user_password(db, test_user):
    from app.core.security import verify_password
    old_hashed = test_user.hashed_password
    
    user_update = UserUpdate(password="newpassword123")
    updated_user = update_user(db, test_user, user_update)
    
    assert updated_user.hashed_password != old_hashed
    assert verify_password("newpassword123", updated_user.hashed_password) is True
    assert verify_password("oldpassword", updated_user.hashed_password) is False

def test_update_user_partial(db, test_user):
    original_first_name = test_user.first_name
    original_last_name = test_user.last_name
    
    user_update = UserUpdate(first_name="Updated")
    updated_user = update_user(db, test_user, user_update)
    
    assert updated_user.first_name == "Updated"
    assert updated_user.last_name == original_last_name
