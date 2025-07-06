import uuid
from pydantic import BaseModel, Field
from app.models.todo import PriorityEnum

class TodoBase(BaseModel):
    title: str
    description: str | None = None
    priority: PriorityEnum = PriorityEnum.MEDIUM

class TodoCreate(TodoBase): pass

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: PriorityEnum | None = None
    completed: bool | None = None
    archived: bool | None = None

class TodoRead(TodoBase):
    id: uuid.UUID
    completed: bool
    archived: bool
    priority: PriorityEnum

    class Config:
        from_attributes = True
