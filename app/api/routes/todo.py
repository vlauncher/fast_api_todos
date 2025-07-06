from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_user_id
from app.schemas.todo import *
from app.services import todo_service

router = APIRouter()

@router.post("/", response_model=TodoRead)
async def create(todo: TodoCreate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await todo_service.create_todo(user_id, todo, db)

@router.get("/", response_model=list[TodoRead])
async def list_todos(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await todo_service.read_todos(user_id, db)

@router.get("/{todo_id}", response_model=TodoRead)
async def get(todo_id: UUID, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await todo_service.read_todo(str(todo_id), user_id, db)

@router.put("/{todo_id}", response_model=TodoRead)
async def update(todo_id: UUID, todo: TodoUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await todo_service.update_todo(str(todo_id), user_id, todo, db)

@router.delete("/{todo_id}")
async def delete(todo_id: UUID, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await todo_service.delete_todo(str(todo_id), user_id, db)
    return {"msg": "Todo deleted"}

@router.patch("/{todo_id}/toggle-completed", response_model=TodoRead)
async def toggle_completed(todo_id: UUID, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await todo_service.toggle_completed(str(todo_id), user_id, db)

@router.patch("/{todo_id}/toggle-archived", response_model=TodoRead)
async def toggle_archived(todo_id: UUID, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await todo_service.toggle_archived(str(todo_id), user_id, db)
