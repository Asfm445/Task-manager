from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from domain.models.task_model import TaskCreateInput, TaskOutput, TaskProgressDomain
from infrastructure.dto.task_dto import (
    domain_to_orm_task_create,
    domain_to_orm_task_progress,
    orm_to_domain_task_output,
    orm_to_domain_task_progress,
)
from infrastructure.models.model import StopProgress, Task, TaskProgress, User


class TaskRepository:
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
        if not task:
            return None
        return orm_to_domain_task_output(task)

    

    async def get_tasks(self, skip: int = 0, limit: int = 100) -> List[TaskOutput]:
        result = await self.db.execute(
            select(Task)
            .options(
                selectinload(Task.assignees),
                selectinload(Task.owner),
                selectinload(Task.subtasks),  # eagerly load subtasks
            )
            .offset(skip)
            .limit(limit)
        )
        tasks = result.scalars().all()  # no await here
        return [orm_to_domain_task_output(task) for task in tasks]


    async def create_task(self, task: TaskCreateInput, owner_id: int) -> TaskOutput:
        db_task = domain_to_orm_task_create(task, owner_id)
        self.db.add(db_task)
        await self.db.commit()
        await self.db.refresh(db_task)
        return orm_to_domain_task_output(db_task)

    async def delete_task(self, task_id: int, owner_id: int):
        result = await self.db.execute(select(Task).filter(Task.id == task_id, Task.owner_id == owner_id))
        task = result.scalar_one_or_none()
        if task:
            await self.db.delete(task)
            await self.db.commit()
            return True
        return False

    async def create_progress(self, progress: TaskProgressDomain) -> TaskProgressDomain:
        db_progress = domain_to_orm_task_progress(progress)
        self.db.add(db_progress)
        await self.db.commit()
        await self.db.refresh(db_progress)
        return orm_to_domain_task_progress(db_progress)

    async def assign_user_to_task(self, task_id: int, assignee_email: str):
        result_task = await self.db.execute(select(Task).filter(Task.id == task_id))
        task = result_task.scalar_one_or_none()
        result_user = await self.db.execute(select(User).filter(User.email == assignee_email))
        user = result_user.scalar_one_or_none()

        if not task or not user:
            return None, "Task or User not found"

        if user in task.assignees:
            return None, "User already assigned"

        task.assignees.append(user)
        await self.db.commit()
        await self.db.refresh(task)
        return orm_to_domain_task_output(task), None

    async def update_task(self, task_id: int, data: dict):
        result = await self.db.execute(select(Task).filter(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            return None

        for key, value in data.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)

        try:
            await self.db.commit()
            await self.db.refresh(task)
        except Exception:
            await self.db.rollback()
            return None

        return orm_to_domain_task_output(task)

    async def create_stop(self, task_id: int):
        db_stop = StopProgress(task_id=task_id, stopped_at=datetime.now(timezone.utc))
        self.db.add(db_stop)
        await self.db.commit()
        await self.db.refresh(db_stop)
        return db_stop

    async def delete_stop(self, task_id: int):
        result = await self.db.execute(select(StopProgress).filter(StopProgress.task_id == task_id))
        stop = result.scalar_one_or_none()
        if not stop:
            return None
        await self.db.delete(stop)
        await self.db.commit()
        return None

    async def get_stop(self, task_id: int):
        result = await self.db.execute(select(StopProgress).filter(StopProgress.task_id == task_id))
        stop = result.scalar_one_or_none()
        return stop

    async def get_progress(self, task_id, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(TaskProgress)
            .filter(TaskProgress.task_id == task_id)
            .offset(skip)
            .limit(limit)
        )
        progress = result.scalars().all()
        return progress
