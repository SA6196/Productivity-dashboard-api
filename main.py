from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from jose import jwt
import logging

import models, schemas, auth
from database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Productivity API")
security = HTTPBearer()

logging.basicConfig(level=logging.INFO)


# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- AUTH ----------------
def get_user(credentials: HTTPAuthorizationCredentials = Depends(security),
             db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(401, "User not found")
        return user
    except:
        raise HTTPException(401, "Invalid token")


# ---------------- REGISTER ----------------
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(400, "User exists")

    new_user = models.User(
        email=user.email,
        password=auth.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    logging.info(f"User registered: {user.email}")
    return {"message": "Registered successfully"}


# ---------------- LOGIN ----------------
@app.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    u = db.query(models.User).filter(models.User.email == user.email).first()
    if not u or not auth.verify_password(user.password, u.password):
        raise HTTPException(401, "Invalid credentials")

    token = auth.create_token({"sub": u.email})
    return {"access_token": token}


# ---------------- CREATE TASK ----------------
@app.post("/tasks")
def create_task(task: schemas.TaskCreate, user=Depends(get_user), db: Session = Depends(get_db)):
    new_task = models.Task(**task.dict(), owner_id=user.id)
    db.add(new_task)
    db.commit()
    logging.info(f"Task created by {user.email}")
    return {"message": "Task created"}


# ---------------- LIST + SEARCH + FILTER ----------------
@app.get("/tasks", response_model=list[schemas.TaskOut])
def list_tasks(
    user=Depends(get_user),
    db: Session = Depends(get_db),
    status: str = None,
    priority: str = None,
    search: str = None
):
    query = db.query(models.Task).filter(models.Task.owner_id == user.id)

    if status:
        query = query.filter(models.Task.status == status)

    if priority:
        query = query.filter(models.Task.priority == priority)

    if search:
        query = query.filter(models.Task.title.contains(search))

    tasks = query.all()

    # auto overdue
    for t in tasks:
        if t.deadline and t.deadline < datetime.utcnow() and t.status != "Completed":
            t.status = "Overdue"

    db.commit()
    return tasks


# ---------------- UPDATE TASK ----------------
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updates: schemas.TaskUpdate,
                user=Depends(get_user), db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == user.id
    ).first()

    if not task:
        raise HTTPException(404, "Task not found")

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Task updated"}


# ---------------- DELETE TASK ----------------
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, user=Depends(get_user), db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == user.id
    ).first()

    if not task:
        raise HTTPException(404, "Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}


# ---------------- DASHBOARD ----------------
@app.get("/dashboard")
def dashboard(user=Depends(get_user), db: Session = Depends(get_db)):
    tasks = db.query(models.Task).filter(models.Task.owner_id == user.id).all()

    total = len(tasks)
    completed = len([t for t in tasks if t.status == "Completed"])
    overdue = len([t for t in tasks if t.status == "Overdue"])
    rate = (completed / total * 100) if total else 0

    return {
        "total_tasks": total,
        "completed": completed,
        "overdue": overdue,
        "completion_rate": round(rate, 2)
    }
