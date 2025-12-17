from app.config import settings
from fastapi import FastAPI, Depends, HTTPException,status
#import fastapi_cdn_host

from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func  
from passlib.context import CryptContext

from . import models, schemas
from .database import SessionLocal, engine

#JWT
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette import status  # 如果你还没导入 status，这里一起补




import logging
logger = logging.getLogger(__name__)

#models.Base.metadata.create_all(bind=engine)

app = FastAPI(title='fastapi todo demo with db')


# 1) 请求参数校验错误（Pydantic 层面）
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    validation_exception_handler:
    处理 body / query / path 参数校验失败的情况。
    """
    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),  # 具体错误列表
            "error_code": "validation_error",
        },
    )

# 2) 业务层显式抛出的 HTTPException（比如 400 / 401 / 404）
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    http_exception_handler:
    处理我们代码里 raise HTTPException(...) 的情况。
    """
    logger.warning(
        "HTTP error %s on %s %s: %s",
        exc.status_code,
        request.method,
        request.url.path,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": "http_error",
        },
    )

# 3) 其它所有未处理异常（兜底）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    global_exception_handler:
    所有没单独处理的异常都会走这里。
    """
    logger.error(
        "Unhandled error on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,  # 打出堆栈
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "internal_error",
        },
    )


# 创建一个名叫 "app" 的 logger
# 名字叫 app_logger / logger，意思就是“给这个应用专用的日志记录器”
logger = logging.getLogger("app")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
#fastapi_cdn_host.patch_docs(app)  #解决静态文件加载问题
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#get password hash和verify password 附近新增JWT相关
def create_access_token(data:dict,expires_delta:timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire}) #添加过期时间
    encoded_jwt = jwt.encode(to_encode,settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

#get_current_user 依赖
def get_current_user(
        token:str = Depends(oauth2_scheme),
        db:Session = Depends(get_db),
)   -> models.UserModel:
    credentials_excpetion = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"www-authenticate":"Bearer"},
    )
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        user_id:str | None =payload.get("sub")
        if user_id is None:
            raise credentials_excpetion
    except JWTError:
        raise credentials_excpetion
    user = db.query(models.UserModel).filter(
        models.UserModel.id == user_id
    ).first()
    if user is None:
        raise credentials_excpetion
    return user

@app.get("/me",response_model=schemas.User)
def read_me(
    current_user:models.UserModel = Depends(get_current_user),
):
    return current_user


def get_password_hash(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    """
    plain_password:用户输入的明文密码
    hashed_password:数据库中存储的哈希密码
    返回: bool,密码是否匹配
    """
    return pwd_context.verify(plain_password,hashed_password)


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
    current_user:models.UserModel = Depends(get_current_user),
):
    
    query = db.query(models.TaskModel).filter(
        models.TaskModel.user_id == current_user.id #只看自己的
    )
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
def create_task(
    task: schemas.TaskCreate, 
    db: Session = Depends(get_db),
    current_user:models.UserModel = Depends(get_current_user),
    ):
    """
    create_task:在数据库中创建一条新的任务记录。
    - 接收前端传来的任务数据(task: TaskCreate)
    - 组装成 TaskModel(真正的 ORM 对象)
    - 绑定当前用户 user_id
    - 保存进数据库并返回
    """
    new_task = models.TaskModel(
        title=task.title,
        description=task.description,
        is_done=task.is_done,
        priority=task.priority,
        user_id=current_user.id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.post("/auth/register",response_model=schemas.User)
def register(user_in:schemas.UserCreate, db:Session = Depends(get_db)):
    
    logger.info("Register attempt: username=%s email=%s", user_in.username, user_in.email)
    # 1.检查用户是否已经存在
    existing = db.query(models.UserModel).filter(
        models.UserModel.username == user_in.username
        ).first()
    if existing:
        raise HTTPException(status_code=400,detail="Username already registered")
    
    #2.构造UserModel,密码使用哈希存储
    hashed_password = get_password_hash(user_in.password)
    user =models.UserModel(
        username = user_in.username,
        email = user_in.email,
        hashed_password = hashed_password,
    )

    #3.写入数据库
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("Register success: user_id=%s username=%s", user.id, user.username)
    return user

@app.post("/auth/login",response_model=schemas.Token)#schemas.User改为schemas.Token
def login(
    form_data:OAuth2PasswordRequestForm = Depends(),
    db:Session = Depends(get_db),
    ):
    """
    login:处理用户登录。
    - 接收表单里的 username/password
    - 去数据库查用户
    - 校验密码
    - 生成并返回 JWT access_token
    """
    user = db.query(models.UserModel).filter(
        models.UserModel.username == form_data.username
    ).first()
    if not user or not verify_password(form_data.password,user.hashed_password):
        raise  HTTPException(status_code=400,detail="Incorrect username or password")
    access_token = create_access_token(data={"sub":user.id})
    return {"access_token":access_token,"token_type":"bearer"}
    # data:schemas.LoginRequest, db:Session = Depends(get_db)):
    # user = db.query(models.UserModel).filter(
    #     models.UserModel.username == data.username
    # ).first()

    # #用户不存在或密码错误
    # if not user :
    #     raise HTTPException(status_code=400,detail="Incorrect username or password")
    # if not verify_password(data.password, user.hashed_password):
    #     raise HTTPException(status_code=400,detail="Incorrect username or password")
    # #修改问返回token而不是user
    # access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token = create_access_token(
    #     data={"sub":user.id},
    #     expires_delta=access_token_expires,
    
    return {"access_token":access_token,"token_type":"bearer"}

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
def get_task(
    task_id:str, 
    db:Session = Depends(get_db),
    current_user:models.UserModel = Depends(get_current_user),
    ):
    task = db.query(models.TaskModel).filter(
        models.TaskModel.id == task_id,
        models.TaskModel.user_id == current_user.id,
        ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: str, 
    task_in: schemas.TaskUpdate, 
    db: Session = Depends(get_db),
    current_user:models.UserModel = Depends(get_current_user),
    ):
    task = db.query(models.TaskModel).filter(
        models.TaskModel.id == task_id,
        models.TaskModel.user_id == current_user.id,
        ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: str, 
    db: Session = Depends(get_db),
    current_user:models.UserModel = Depends(get_current_user),
    ):
    task = db.query(models.TaskModel).filter(
        models.TaskModel.id == task_id,
        models.TaskModel.user_id == current_user.id,
        ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"ok": True}

