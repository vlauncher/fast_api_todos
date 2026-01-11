import datetime
from app.models import User, Todo

def test_user_model_creation(db):
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        first_name="Test",
        last_name="User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.is_active is True
    assert user.is_verified is False
    assert user.created_at is not None

def test_user_model_otp_fields(db):
    from app.core.security import get_password_hash, generate_otp
    
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
    
    assert user.otp_code == otp
    assert user.otp_created_at is not None

def test_user_model_relationship(db):
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        first_name="Test",
        last_name="User",
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    todo = Todo(
        title="Test Todo",
        description="Test Description",
        user_id=user.id
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    
    assert len(user.todos) == 1
    assert user.todos[0].title == "Test Todo"
    assert todo.owner == user

def test_todo_model_creation(db):
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        first_name="Test",
        last_name="User",
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    todo = Todo(
        title="Test Todo",
        description="Test Description",
        user_id=user.id
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    
    assert todo.id is not None
    assert todo.title == "Test Todo"
    assert todo.description == "Test Description"
    assert todo.is_completed is False
    assert todo.is_archived is False
    assert todo.user_id == user.id
    assert todo.created_at is not None
    assert todo.updated_at is not None

def test_todo_model_optional_fields(db):
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        first_name="Test",
        last_name="User",
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    todo = Todo(
        title="Test Todo",
        user_id=user.id
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    
    assert todo.description is None
    assert todo.is_completed is False
    assert todo.is_archived is False

def test_todo_model_update(db):
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        first_name="Test",
        last_name="User",
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    todo = Todo(
        title="Test Todo",
        user_id=user.id
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    
    original_updated_at = todo.updated_at
    
    todo.is_completed = True
    todo.is_archived = True
    db.commit()
    db.refresh(todo)
    
    assert todo.is_completed is True
    assert todo.is_archived is True
    assert todo.updated_at >= original_updated_at
