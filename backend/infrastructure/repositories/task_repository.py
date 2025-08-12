from datetime import datetime, timezone
from typing import List

from domain.models.task_model import TaskCreateInput, TaskOutput, TaskProgressDomain
from infrastructure.dto.task_dto import (
    domain_to_orm_task_create,
    domain_to_orm_task_progress,
    orm_to_domain_task_output,
    orm_to_domain_task_progress,
)
from infrastructure.models.model import StopProgress, Task, TaskProgress, User
from sqlalchemy.orm import Session


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_task(self, task_id: int) -> TaskOutput:
        result = self.db.query(Task).filter(Task.id == task_id).first()
        if not result:
            return None
        return orm_to_domain_task_output(result)

    def get_tasks(self, skip: int = 0, limit: int = 100) -> List[TaskOutput]:
        result = self.db.query(Task).offset(skip).limit(limit).all()
        return [orm_to_domain_task_output(task) for task in result]

    def create_task(self, task: TaskCreateInput, owner_id: int) -> TaskOutput:
        db_task = domain_to_orm_task_create(task, owner_id)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return orm_to_domain_task_output(db_task)

    def delete_task(self, task_id: int, owner_id: int):
        task = (
            self.db.query(Task)
            .filter(Task.id == task_id, Task.owner_id == owner_id)
            .first()
        )
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False

    def create_progress(self, progress: TaskProgressDomain) -> TaskProgressDomain:
        db_progress = domain_to_orm_task_progress(progress)
        self.db.add(db_progress)
        self.db.commit()
        self.db.refresh(db_progress)
        return orm_to_domain_task_progress(db_progress)

    # repositories/task_repo.py

    def assign_user_to_task(self, task_id: int, assignee_email: str):
        task = self.db.query(Task).filter(Task.id == task_id).first()
        user = self.db.query(User).filter(User.email == assignee_email).first()

        if not task or not user:
            return None, "Task or User not found"

        if user in task.assignees:
            return None, "User already assigned"

        task.assignees.append(user)
        self.db.commit()
        self.db.refresh(task)
        return orm_to_domain_task_output(task)

    def update_task(self, task_id: int, data: dict):
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None, "Task not found"

        for key, value in data.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)

        try:
            self.db.commit()
            self.db.refresh(task)
        except Exception as e:
            self.db.rollback()
            return None, f"Update failed: {str(e)}"

        return orm_to_domain_task_output(task)

    def create_stop(self, task_id):
        db_stop = StopProgress(task_id=task_id, stopped_at=datetime.now(timezone.utc))
        self.db.add(db_stop)
        self.db.commit()
        self.db.refresh(db_stop)
        return db_stop

    def delete_stop(self, task_id):
        stop = (
            self.db.query(StopProgress).filter(StopProgress.task_id == task_id).first()
        )
        if not stop:
            return None
        self.db.delete(stop)
        self.db.commit()
        return None

    def get_stop(self, task_id):
        stop = (
            self.db.query(StopProgress).filter(StopProgress.task_id == task_id).first()
        )
        if not stop:
            return None
        return stop

    def get_progress(self, task_id, skip: int = 0, limit: int = 100):
        return (
            self.db.query(TaskProgress)
            .filter(TaskProgress.task_id == task_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
