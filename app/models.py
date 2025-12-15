from sqlalchemy import Column, String, Boolean, DateTime, Integer,ForeignKey
from sqlalchemy.orm import relationship   
from datetime import datetime
import uuid

from .database import Base

def generate_uuid():
    return str(uuid.uuid4())
class TaskModel(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    priority = Column(Integer, default=1)
    #外键，指向users表
    user_id = Column(String, ForeignKey("users.id"),nullable=True)
    #反向关系，指回UserModel
    user = relationship("UserModel",back_populates="tasks")


class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True,index=True,default=lambda:str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True ,index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default = datetime.utcnow)

    tasks = relationship("TaskModel",back_populates="user",cascade="all,delete-orphan")
