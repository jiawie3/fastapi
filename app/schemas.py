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

class UserBase(BaseModel):
    username:str = Field(...,min_length=3,max_length=20)
    email: Optional[str] = Field(None, max_length=50)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=20)
class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
#新增 登录请求体
class LoginRequest(BaseModel):
    username: str
    password: str

#新增 登陆成功后返回的token
class Token(BaseModel):
    access_token:str
    token_type:str = "bearer"
#新增 解析token里的数据时用
class TokenDaTa(BaseModel):
    user_id: Optional[str] = None
