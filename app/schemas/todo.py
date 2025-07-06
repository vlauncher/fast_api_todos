from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TodoBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    priority: PriorityEnum = PriorityEnum.medium


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    priority: Optional[PriorityEnum]
    completed: Optional[bool]
    archived: Optional[bool]


class TodoRead(TodoBase):
    id: str
    completed: bool
    archived: bool

    class Config:
        from_attributes = True
