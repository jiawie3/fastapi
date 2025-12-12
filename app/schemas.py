from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TaskBase(BaseModel):
    title:str = Field(...,min_length=1,max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_done: bool = False
    priority: int = Field(1, ge=1, le=2000)
    # title: str
    # description: Optional[str] = None
    # is_done: bool = False
    # priority: int = 1

class TaskCreate(TaskBase):
    pass     
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_done: Optional[bool] = None
    priority: Optional[int] = None
class Task(TaskBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
class Taskstats(BaseModel):
    total: int
    done: int
    undone: int
    high_priority: int

    