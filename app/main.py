from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func  

from . import models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title='fastapi todo demo with db')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tasks",response_model=list[schemas.Task])
def list_tasks(
    done:Optional[bool] = None,

    keyword:Optional[str] = None,
    skip : int = 0,
    limit : int = 10,

    db:Session = Depends(get_db),
):
    query = db.query(models.TaskModel)
    if done is not None:
        query = query.filter(models.TaskModel.is_done == done)
    
    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            models.TaskModel.title.ilike(like_pattern) |
            models.TaskModel.description.ilike(like_pattern)
        )
        
    query = query.order_by(
        models.TaskModel.created_at.desc(),
        models.TaskModel.priority.desc(),
        )
    
    query = query.offset(skip).limit(limit)
    tasks = query.all()
    return tasks


@app.post("/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = models.TaskModel(
        title=task.title,
        description=task.description,
        is_done=task.is_done,
        priority=task.priority
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks/stats", response_model=schemas.Taskstats)
def get_task_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(models.TaskModel.id)).scalar()
    done = db.query(func.count(models.TaskModel.id)).filter(models.TaskModel.is_done == True).scalar()
    undone = total - done
    high_priority = db.query(func.count(models.TaskModel.id)).filter(models.TaskModel.priority >= 5).scalar()
    return schemas.Taskstats(
        total=total,
        done=done,
        undone=undone,
        high_priority=high_priority
    )


@app.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task(task_id:str, db:Session = Depends(get_db)):
    task = db.query(models.TaskModel).filter(models.TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: str, task_in: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.TaskModel).filter(models.TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task



@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(models.TaskModel).filter(models.TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"ok": True}