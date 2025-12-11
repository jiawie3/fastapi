from sqlalchemy import Column, String, Boolean, DateTime, Integer   
from datetime import datetime
from .database import Base
import uuid
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
