from infrastructure.models.model import Task, TaskProgress, User
from sqlalchemy.orm import Session


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_task(self, task_id: int):
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_tasks(self, skip: int = 0, limit: int = 100):
        return self.db.query(Task).offset(skip).limit(limit).all()

    def create_task(self, task: dict):
        db_task = Task(**task)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

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

    def create_progress(self, progress: dict):
        db_progress = TaskProgress(**progress)
        self.db.add(db_progress)
        self.db.commit()
        self.db.refresh(db_progress)
        return db_progress

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
        return task, None

    def update_task(self, task_id: int, data: dict):
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None, "Task not found"

        for key, value in data.items():
            if hasattr(task, key):
                setattr(task, key, value)

        try:
            self.db.commit()
            self.db.refresh(task)
        except Exception as e:
            self.db.rollback()
            return None, f"Update failed: {str(e)}"

        return task
