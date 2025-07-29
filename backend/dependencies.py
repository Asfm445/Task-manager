from fastapi import Depends
from infrastructure.db.session import SessionLocal
from infrastructure.repositories.task_repository import TaskRepository

# from fastapi import Depends
from services.task_service import TaskService
from sqlalchemy.orm import Session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    repo = TaskRepository(db)
    return TaskService(repo)
