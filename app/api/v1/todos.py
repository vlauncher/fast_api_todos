from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas import Todo, TodoCreate, TodoUpdate
from app.services import create_todo, delete_todo, get_todo_by_id, get_todos_by_user, toggle_todo_archive, toggle_todo_complete, update_todo

router = APIRouter(prefix="/todos", tags=["Todos"])

@router.post("/", response_model=Todo, summary="Create new todo")
def create_todo_endpoint(
    todo: TodoCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_todo(db, todo, current_user.id)

@router.get("/", response_model=List[Todo], summary="List todos")
def read_todos(
    skip: int = 0, 
    limit: int = 100, 
    archived: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_todos_by_user(db, current_user.id, skip, limit, archived)

@router.get("/{todo_id}", response_model=Todo, summary="Get single todo")
def read_todo(
    todo_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todo = get_todo_by_id(db, todo_id, current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=Todo, summary="Update todo")
def update_todo_endpoint(
    todo_id: int, 
    todo_update: TodoUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todo = get_todo_by_id(db, todo_id, current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return update_todo(db, todo, todo_update)

@router.patch("/{todo_id}/complete", response_model=Todo, summary="Toggle todo completion")
def toggle_complete(
    todo_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todo = get_todo_by_id(db, todo_id, current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return toggle_todo_complete(db, todo)

@router.patch("/{todo_id}/archive", response_model=Todo, summary="Toggle todo archive")
def toggle_archive(
    todo_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todo = get_todo_by_id(db, todo_id, current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return toggle_todo_archive(db, todo)

@router.delete("/{todo_id}", summary="Delete todo")
def delete_todo_endpoint(
    todo_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todo = get_todo_by_id(db, todo_id, current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    delete_todo(db, todo)
    return {"message": "Todo deleted successfully"}
