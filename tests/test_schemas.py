import datetime
import pytest
from pydantic import ValidationError
from app.schemas import (
    User, UserBase, UserCreate, UserUpdate,
    Todo, TodoBase, TodoCreate, TodoUpdate,
    Token, TokenData, UserVerify, PasswordChange,
    PasswordResetRequest, PasswordResetConfirm
)

def test_user_base_schema():
    user_base = UserBase(
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    assert user_base.email == "test@example.com"
    assert user_base.first_name == "Test"
    assert user_base.last_name == "User"

def test_user_create_schema():
    user_create = UserCreate(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password="testpass123"
    )
    assert user_create.email == "test@example.com"
    assert user_create.password == "testpass123"

def test_user_update_schema():
    user_update = UserUpdate(
        first_name="Updated",
        last_name="Name",
        password="newpass123"
    )
    assert user_update.first_name == "Updated"
    assert user_update.last_name == "Name"
    assert user_update.password == "newpass123"

def test_user_update_schema_partial():
    user_update = UserUpdate(first_name="Updated")
    assert user_update.first_name == "Updated"
    assert user_update.last_name is None
    assert user_update.password is None

def test_user_schema_from_attributes():
    user_dict = {
        "id": 1,
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.datetime.now(datetime.timezone.utc)
    }
    user = User(**user_dict)
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.is_verified is False

def test_todo_base_schema():
    todo_base = TodoBase(
        title="Test Todo",
        description="Test Description"
    )
    assert todo_base.title == "Test Todo"
    assert todo_base.description == "Test Description"

def test_todo_base_schema_optional_description():
    todo_base = TodoBase(title="Test Todo")
    assert todo_base.title == "Test Todo"
    assert todo_base.description is None

def test_todo_create_schema():
    todo_create = TodoCreate(
        title="Test Todo",
        description="Test Description"
    )
    assert todo_create.title == "Test Todo"
    assert todo_create.description == "Test Description"

def test_todo_update_schema():
    todo_update = TodoUpdate(
        title="Updated Todo",
        description="Updated Description",
        is_completed=True,
        is_archived=True
    )
    assert todo_update.title == "Updated Todo"
    assert todo_update.is_completed is True
    assert todo_update.is_archived is True

def test_todo_update_schema_partial():
    todo_update = TodoUpdate(is_completed=True)
    assert todo_update.is_completed is True
    assert todo_update.title is None
    assert todo_update.description is None

def test_todo_schema_from_attributes():
    todo_dict = {
        "id": 1,
        "title": "Test Todo",
        "description": "Test Description",
        "is_completed": False,
        "is_archived": False,
        "user_id": 1,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "updated_at": datetime.datetime.now(datetime.timezone.utc)
    }
    todo = Todo(**todo_dict)
    assert todo.id == 1
    assert todo.title == "Test Todo"
    assert todo.is_completed is False
    assert todo.user_id == 1

def test_token_schema():
    token = Token(
        access_token="access_token_value",
        refresh_token="refresh_token_value",
        token_type="bearer"
    )
    assert token.access_token == "access_token_value"
    assert token.refresh_token == "refresh_token_value"
    assert token.token_type == "bearer"

def test_token_data_schema():
    token_data = TokenData(email="test@example.com")
    assert token_data.email == "test@example.com"

def test_token_data_schema_optional():
    token_data = TokenData()
    assert token_data.email is None

def test_user_verify_schema():
    user_verify = UserVerify(
        email="test@example.com",
        otp="123456"
    )
    assert user_verify.email == "test@example.com"
    assert user_verify.otp == "123456"

def test_password_change_schema():
    password_change = PasswordChange(
        old_password="oldpass123",
        new_password="newpass123"
    )
    assert password_change.old_password == "oldpass123"
    assert password_change.new_password == "newpass123"

def test_password_reset_request_schema():
    request = PasswordResetRequest(email="test@example.com")
    assert request.email == "test@example.com"

def test_password_reset_confirm_schema():
    confirm = PasswordResetConfirm(
        email="test@example.com",
        otp="123456",
        new_password="newpass123"
    )
    assert confirm.email == "test@example.com"
    assert confirm.otp == "123456"
    assert confirm.new_password == "newpass123"
