from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Todo
from app.schemas import TodoCreate, TodoUpdate

def get_todos_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100, archived: Optional[bool] = None) -> List[Todo]:
    query = db.query(Todo).filter(Todo.user_id == user_id)
    if archived is not None:
        query = query.filter(Todo.is_archived == archived)
    return query.offset(skip).limit(limit).all()

def get_todo_by_id(db: Session, todo_id: int, user_id: int) -> Todo | None:
    return db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user_id).first()

def create_todo(db: Session, todo: TodoCreate, user_id: int) -> Todo:
    new_todo = Todo(**todo.model_dump(), user_id=user_id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

def update_todo(db: Session, todo: Todo, todo_update: TodoUpdate) -> Todo:
    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)
    
    db.commit()
    db.refresh(todo)
    return todo

def toggle_todo_complete(db: Session, todo: Todo) -> Todo:
    todo.is_completed = not todo.is_completed
    db.commit()
    db.refresh(todo)
    return todo

def toggle_todo_archive(db: Session, todo: Todo) -> Todo:
    todo.is_archived = not todo.is_archived
    db.commit()
    db.refresh(todo)
    return todo

def delete_todo(db: Session, todo: Todo) -> None:
    db.delete(todo)
    db.commit()
