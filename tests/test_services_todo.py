import pytest
from app.schemas import TodoCreate, TodoUpdate
from app.services.todo_service import (
    get_todos_by_user,
    get_todo_by_id,
    create_todo,
    update_todo,
    toggle_todo_complete,
    toggle_todo_archive,
    delete_todo
)

def test_get_todos_by_user(db, test_user, test_todo):
    todos = get_todos_by_user(db, test_user.id)
    assert len(todos) == 1
    assert todos[0].id == test_todo.id
    assert todos[0].title == test_todo.title

def test_get_todos_by_user_multiple(db, test_user):
    todo1 = create_todo(db, TodoCreate(title="Todo 1"), test_user.id)
    todo2 = create_todo(db, TodoCreate(title="Todo 2"), test_user.id)
    todo3 = create_todo(db, TodoCreate(title="Todo 3"), test_user.id)
    
    todos = get_todos_by_user(db, test_user.id)
    assert len(todos) == 3

def test_get_todos_by_user_with_pagination(db, test_user):
    for i in range(5):
        create_todo(db, TodoCreate(title=f"Todo {i}"), test_user.id)
    
    todos = get_todos_by_user(db, test_user.id, skip=0, limit=2)
    assert len(todos) == 2
    
    todos = get_todos_by_user(db, test_user.id, skip=2, limit=2)
    assert len(todos) == 2

def test_get_todos_by_user_archived_filter(db, test_user):
    todo1 = create_todo(db, TodoCreate(title="Active Todo"), test_user.id)
    todo2 = create_todo(db, TodoCreate(title="Archived Todo"), test_user.id)
    toggle_todo_archive(db, todo2)
    
    active_todos = get_todos_by_user(db, test_user.id, archived=False)
    archived_todos = get_todos_by_user(db, test_user.id, archived=True)
    
    assert len(active_todos) == 1
    assert len(archived_todos) == 1
    assert active_todos[0].id == todo1.id
    assert archived_todos[0].id == todo2.id

def test_get_todo_by_id(db, test_user, test_todo):
    todo = get_todo_by_id(db, test_todo.id, test_user.id)
    assert todo is not None
    assert todo.id == test_todo.id
    assert todo.title == test_todo.title

def test_get_todo_by_id_not_found(db, test_user):
    todo = get_todo_by_id(db, 99999, test_user.id)
    assert todo is None

def test_get_todo_by_id_wrong_user(db, test_user):
    from app.core.security import get_password_hash, generate_otp
    import datetime
    
    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("testpass"),
        first_name="Other",
        last_name="User",
        is_verified=True
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    
    todo = create_todo(db, TodoCreate(title="Other User Todo"), other_user.id)
    
    result = get_todo_by_id(db, todo.id, test_user.id)
    assert result is None

def test_create_todo(db, test_user):
    todo_data = TodoCreate(
        title="New Todo",
        description="New Description"
    )
    todo = create_todo(db, todo_data, test_user.id)
    assert todo.id is not None
    assert todo.title == "New Todo"
    assert todo.description == "New Description"
    assert todo.user_id == test_user.id
    assert todo.is_completed is False
    assert todo.is_archived is False

def test_create_todo_without_description(db, test_user):
    todo_data = TodoCreate(title="New Todo")
    todo = create_todo(db, todo_data, test_user.id)
    assert todo.title == "New Todo"
    assert todo.description is None

def test_update_todo(db, test_user, test_todo):
    todo_update = TodoUpdate(
        title="Updated Todo",
        description="Updated Description",
        is_completed=True
    )
    updated_todo = update_todo(db, test_todo, todo_update)
    assert updated_todo.title == "Updated Todo"
    assert updated_todo.description == "Updated Description"
    assert updated_todo.is_completed is True

def test_update_todo_partial(db, test_user, test_todo):
    original_description = test_todo.description
    todo_update = TodoUpdate(title="Updated Title")
    updated_todo = update_todo(db, test_todo, todo_update)
    assert updated_todo.title == "Updated Title"
    assert updated_todo.description == original_description

def test_toggle_todo_complete(db, test_user, test_todo):
    assert test_todo.is_completed is False
    
    toggled = toggle_todo_complete(db, test_todo)
    assert toggled.is_completed is True
    
    toggled_again = toggle_todo_complete(db, toggled)
    assert toggled_again.is_completed is False

def test_toggle_todo_archive(db, test_user, test_todo):
    assert test_todo.is_archived is False
    
    toggled = toggle_todo_archive(db, test_todo)
    assert toggled.is_archived is True
    
    toggled_again = toggle_todo_archive(db, toggled)
    assert toggled_again.is_archived is False

def test_delete_todo(db, test_user, test_todo):
    todo_id = test_todo.id
    delete_todo(db, test_todo)
    
    deleted_todo = get_todo_by_id(db, todo_id, test_user.id)
    assert deleted_todo is None
