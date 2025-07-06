from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import UUID
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate

async def create_todo(user_id: str, todo_in: TodoCreate, db: AsyncSession):
    todo = Todo(**todo_in.model_dump(), user_id=user_id)
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return todo

async def read_todos(user_id: str, db: AsyncSession):
    result = await db.execute(select(Todo).where(Todo.user_id == UUID(user_id)))
    return result.scalars().all()

async def read_todo(todo_id: str, user_id: str, db: AsyncSession):
    result = await db.execute(select(Todo).where(Todo.id == todo_id, Todo.user_id == UUID(user_id)))
    todo = result.scalar()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

async def update_todo(todo_id: str, user_id: str, todo_in: TodoUpdate, db: AsyncSession):
    todo = await read_todo(todo_id, user_id, db)
    for field, value in todo_in.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    await db.commit()
    await db.refresh(todo)
    return todo

async def delete_todo(todo_id: str, user_id: str, db: AsyncSession):
    todo = await read_todo(todo_id, user_id, db)
    await db.delete(todo)
    await db.commit()

async def toggle_completed(todo_id: str, user_id: str, db: AsyncSession):
    todo = await read_todo(todo_id, user_id, db)
    todo.completed = not todo.completed
    await db.commit()
    return todo

async def toggle_archived(todo_id: str, user_id: str, db: AsyncSession):
    todo = await read_todo(todo_id, user_id, db)
    todo.archived = not todo.archived
    await db.commit()
    return todo
