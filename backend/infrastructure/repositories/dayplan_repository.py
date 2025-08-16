from datetime import date

from domain.exceptions import BadRequestError, NotFoundError
from domain.models.dayplan_model import TimeLog as dTimeLog
from domain.repositories.dayplan_repo import AbstractDayPlanRepository
from domain.repositories.task_repo import AbstractTaskRepository
from infrastructure.dto.dayplan_dto import (
    domain_to_orm_timelog,
    orm_to_domain_dayplan,
    orm_to_domain_timelog,
)
from infrastructure.models.model import DayPlan, TimeLog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class DayPlanRepository(AbstractDayPlanRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_dayplan(self, date: date, current_user) -> DayPlan:
        dayplan = DayPlan(date=date, user_id=current_user.id)
        self.db.add(dayplan)
        await self.db.commit()
        await self.db.refresh(dayplan)
        return orm_to_domain_dayplan(dayplan)

    async def get_dayplan(self, date: date, current_user) -> DayPlan:
        result = await self.db.execute(
            select(DayPlan).filter(
                DayPlan.date == date, DayPlan.user_id == current_user.id
            )
        )
        dayplan = result.scalars().first()
        if not dayplan:
            return None
        return orm_to_domain_dayplan(dayplan)

    async def get_dayplanById(self, id: int) -> DayPlan:
        result = await self.db.execute(select(DayPlan).filter(DayPlan.id == id))
        dayplan = result.scalars().first()
        if not dayplan:
            return None
        return orm_to_domain_dayplan(dayplan)

    async def delete_dayplan(self, date: date, current_user) -> DayPlan:
        dayplan = await self.get_dayplan(date, current_user)
        self.db.delete(dayplan)
        await self.db.commit()
        return orm_to_domain_dayplan(dayplan)

    async def deleteTimeLog(self, id):
        result = await self.db.execute(select(TimeLog).filter(TimeLog.id == id))
        time_log = result.scalars().first()
        if not time_log:
            return None
        deleted_object=orm_to_domain_timelog(time_log)
        await self.db.delete(time_log)

        await self.db.commit()
        
        return deleted_object

    async def create_time_log(self, time_log: dTimeLog):
        db_time_log = domain_to_orm_timelog(time_log)
        self.db.add(db_time_log)
        await self.db.commit()
        await self.db.refresh(db_time_log)
        return orm_to_domain_timelog(db_time_log)

    async def get_time_log(self, id):
        result = await self.db.execute(select(TimeLog).filter(TimeLog.id == id))
        time_log = result.scalars().first()
        if not time_log:
            return None
        return orm_to_domain_timelog(time_log)

    async def mark_timelog_success(
        self, timelog_id: int, duration: float, task_repo: AbstractTaskRepository
    ):
        async with self.db.begin_nested():
            time_log = await self.get_time_log(timelog_id)
            if not time_log:
                raise NotFoundError("Time log not found")

            task = time_log.task
            task.done_hr += duration

            while task and task.done_hr >= task.estimated_hr:
                data = {"done_hr": task.done_hr, "status": "completed"}
                task = await task_repo.update_task(task.id, data)
                if not task:
                    raise BadRequestError("Task update failed")

                if task.main_task_id:
                    sb_task_es_hr = task.estimated_hr
                    task = await task_repo.get_task(task.main_task_id)
                    task.done_hr += sb_task_es_hr
                else:
                    break
            else:
                if task.status == "pending":
                    await task_repo.update_task(
                        task.id, {"done_hr": task.done_hr, "status": "in_progress"}
                    )

            return time_log
