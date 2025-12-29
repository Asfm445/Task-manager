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

from infrastructure.models.model import StopProgress, Task, TaskProgress, User, task_assignees
from sqlalchemy import and_, or_, exists, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class TaskRepository(AbstractTaskRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_task(self, task_id: int) -> Optional[TaskOutput]:
        result = await self.db.execute(
            select(Task)
            .filter(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        return orm_to_domain_task_output(task) if task else None

    async def get_tasks(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: Optional[int] = None, 
        fetch_all: bool = False, 
        search_name: str = '',
        uncompleted: bool = False,
        completed: bool = False
    ) -> List[TaskOutput]:
        
        # 1. Use EXISTS instead of IN for the subquery (usually faster in Postgres)
        assignee_exists = exists().where(
            and_(
                task_assignees.c.task_id == Task.id,
                task_assignees.c.user_id == user_id
            )
        )

        # Base query: Ownership or Assignment
        query = select(Task).where(or_(Task.owner_id == user_id, assignee_exists))

        if not fetch_all:
            # 2. Optimized Status Filtering
            if completed ^ uncompleted:  # XOR: only if exactly one is True
                status_filter = "completed" if completed else "uncompleted" # adjust logic if needed
                if completed:
                    query = query.where(Task.status == "completed")
                else:
                    query = query.where(Task.status != "completed")

            # 3. Optimized Search
            if search_name:
                words = [f"%{w}%" for w in search_name.split() if w]
                if words:
                    # Combining with AND often yields better results for searches, 
                    # but staying with OR as per your original logic:
                    query = query.where(or_(*(Task.description.ilike(w) for w in words)))

        # 4. Pagination
        query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)

        # 5. Execution Optimization
        result = await self.db.execute(query)
        
        # Use unique() if you have joins to prevent duplicate objects, 
        # though not strictly needed for this specific query.
        tasks = result.scalars().unique().all() 
        
        return [orm_to_domain_task_output(task) for task in tasks]
    

    async def get_assignees_of_task(self, task_id: int) -> List[int]:
        result = await self.db.execute(
            select(task_assignees.c.user_id).where(task_assignees.c.task_id == task_id)
        )
        return [row[0] for row in result.fetchall()]
    
    async def get_assignees_of_task_email(self, task_id: int) -> List[str]:
        result = await self.db.execute(
            select(User.email).where(task_assignees.c.task_id == task_id)
        )
        return [row[0] for row in result.fetchall()]


    async def get_desription_and_id_of_subtasks(self, task_id: int) -> List[str]:
        result = await self.db.execute(
            select(Task.description, Task.id).where(Task.main_task_id == task_id)
        )
        return result.fetchall()
    
        


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
        assignee_exists = exists().where(
            and_(
                task_assignees.c.task_id == task_id,
                task_assignees.c.user_id == user.id
            )
        )

        exist=await self.db.execute(select(assignee_exists))
        if exist.scalar_one():
            return None, "User is already an assignee of this task"
        
        await self.db.execute(task_assignees.insert().values(task_id=task_id, user_id=user.id))
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
            .filter(TaskProgress.task_id == task_id).order_by(TaskProgress.end_date.desc())
            .offset(skip)
            .limit(limit)
        )
        total = await self.db.execute(
            select(func.count(TaskProgress.id)).filter(TaskProgress.task_id == task_id)
        )
        return {"total": total.scalar_one(), "data": [ orm_to_domain_task_progress(progress)  for progress in result.scalars().all()]}
    



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