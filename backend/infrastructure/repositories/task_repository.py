from datetime import datetime, timezone
from typing import List, Optional

from domain.interfaces.task_repo import AbstractTaskRepository
from domain.models.task_model import TaskCreateInput, TaskOutput, TaskProgressDomain
from infrastructure.dto.task_dto import (
    domain_to_orm_task_create,
    domain_to_orm_task_progress,
    orm_to_domain_task_output,
    orm_to_domain_task_progress,
)
from infrastructure.models.model import StopProgress, Task, TaskProgress, User
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class TaskRepository(AbstractTaskRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_task(self, task_id: int) -> Optional[TaskOutput]:
        result = await self.db.execute(
            select(Task)
            .options(
                selectinload(Task.subtasks),
                selectinload(Task.assignees)
            )
            .filter(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        return orm_to_domain_task_output(task) if task else None

    async def get_tasks(self, skip: int = 0, limit: int = 100) -> List[TaskOutput]:
        result = await self.db.execute(
            select(Task).filter(Task.status!="completed")
            .options(
                selectinload(Task.assignees),
                selectinload(Task.owner),
                selectinload(Task.subtasks),
            )
            .offset(skip)
            .limit(limit)
        )
        tasks = result.scalars().all()
        return [orm_to_domain_task_output(task) for task in tasks]

    async def create_task(self, task: TaskCreateInput, owner_id: int) -> TaskOutput:
        db_task = domain_to_orm_task_create(task, owner_id)
        self.db.add(db_task)
        await self.db.flush()
        await self.db.refresh(db_task)
        return orm_to_domain_task_output(db_task)

    async def delete_task(self, task_id: int, owner_id: int) -> bool:
        result = await self.db.execute(
            select(Task).filter(Task.id == task_id, Task.owner_id == owner_id)
        )
        if task := result.scalar_one_or_none():
            await self.db.delete(task)
            await self.db.flush()
            return True
        return False

    async def create_progress(self, progress: TaskProgressDomain) -> TaskProgressDomain:
        db_progress = domain_to_orm_task_progress(progress)
        self.db.add(db_progress)
        await self.db.flush()
        await self.db.refresh(db_progress)
        return orm_to_domain_task_progress(db_progress)

    async def assign_user_to_task(self, task_id: int, assignee_email: str):
        task = (await self.db.execute(
            select(Task).filter(Task.id == task_id)
        )).scalar_one_or_none()
        
        user = (await self.db.execute(
            select(User).filter(User.email == assignee_email)
        )).scalar_one_or_none()

        if not task or not user:
            return None, "Task or User not found"
        if user in task.assignees:
            return None, "User already assigned"

        task.assignees.append(user)
        await self.db.flush()
        await self.db.refresh(task)
        return orm_to_domain_task_output(task), None

    async def update_task(self, task_id: int, data: dict):
        # raise ValueError("task error")
        if task := (await self.db.execute(
            select(Task).filter(Task.id == task_id)
        )).scalar_one_or_none():
            for key, value in data.items():
                if hasattr(task, key) and value is not None:
                    setattr(task, key, value)
            await self.db.flush()
            await self.db.refresh(task)
            return orm_to_domain_task_output(task)
        return None

    async def create_stop(self, task_id: int):
        # raise ValueError("test error")
        db_stop = StopProgress(task_id=task_id, stopped_at=datetime.now(timezone.utc))
        self.db.add(db_stop)
        await self.db.flush()
        await self.db.refresh(db_stop)
        return db_stop

    async def delete_stop(self, task_id: int):
        if stop := (await self.db.execute(
            select(StopProgress).filter(StopProgress.task_id == task_id)
        )).scalar_one_or_none():
            await self.db.delete(stop)
            await self.db.flush()
        return None

    async def get_stop(self, task_id: int):
        return (await self.db.execute(
            select(StopProgress).filter(StopProgress.task_id == task_id)
        )).scalar_one_or_none()

    async def get_progress(self, task_id: int, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(TaskProgress)
            .filter(TaskProgress.task_id == task_id)
            .offset(skip)
            .limit(limit)
        )
        return [ domain_to_orm_task_progress(progress)  for progress in result.scalars().all()]
    



    async def get_tasks_by_name(self, name: str, skip: int = 0, limit: int = 100):
        words = name.split()
        conditions = [Task.description.ilike(f"%{w}%") for w in words]

        query = (
            select(Task)
            .options(
                selectinload(Task.assignees),
                selectinload(Task.owner),
                selectinload(Task.subtasks),
            )
            .filter(and_(*conditions))  # must contain all words
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        tasks = result.scalars().all()
        return [orm_to_domain_task_output(task) for task in tasks]