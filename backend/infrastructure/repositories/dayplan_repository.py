from datetime import date

from domain.interfaces.dayplan_repo import AbstractDayPlanRepository
from domain.models.dayplan_model import TimeLog, TimeLogCreate
from domain.models.dayplan_model import TimeLog as dTimeLog
from infrastructure.dto.dayplan_dto import (
    domain_to_orm_timelog_create,
    orm_to_domain_dayplan,
    orm_to_domain_timelog,
)
from infrastructure.models.model import DayPlan, TimeLog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class DayPlanRepository(AbstractDayPlanRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------
    # DayPlan Methods
    # ------------------------------
    async def create_dayplan(self, date: date, current_user) -> DayPlan:
        dayplan = DayPlan(date=date, user_id=current_user.id)
        self.db.add(dayplan)
        # No commit here
        await self.db.flush()  # Ensure id is generated
        return DayPlan(
            id=dayplan.id,
            date=dayplan.date,
            user_id=dayplan.user_id,
            times=[],
        )

    
    async def get_dayplan(self, date: date, current_user) -> DayPlan | None:
        result = await self.db.execute(
            select(DayPlan)
            .options(
                selectinload(DayPlan.times)            # ✅ load all timelogs
                .selectinload(TimeLog.task)          # ✅ and each timelog’s task
            )
            .filter(DayPlan.date == date, DayPlan.user_id == current_user.id)
        )
        orm_dayplan = result.scalars().first()
        if not orm_dayplan:
            return None
        return orm_to_domain_dayplan(orm_dayplan)

    async def get_dayplanById(self, id: int) -> DayPlan:
        result = await self.db.execute(select(DayPlan).filter(DayPlan.id == id))
        dayplan = result.scalars().first()
        if not dayplan:
            return None
        return orm_to_domain_dayplan(dayplan)

    async def delete_dayplan(self, date: date, current_user) -> DayPlan | None:
        result = await self.db.execute(
            select(DayPlan).filter(
                DayPlan.date == date, DayPlan.user_id == current_user.id
            )
        )
        orm_dayplan = result.scalars().first()
        if orm_dayplan:
            await self.db.delete(orm_dayplan)   # delete ORM object
            return orm_to_domain_dayplan(orm_dayplan)
        return None


    # ------------------------------
    # TimeLog Methods
    # ------------------------------
    async def deleteTimeLog(self, id):
        result = await self.db.execute(select(TimeLog).filter(TimeLog.id == id))
        time_log = result.scalars().first()
        if not time_log:
            return None
        await self.db.delete(time_log)
        await self.db.flush()
        # No commit
        return orm_to_domain_timelog(time_log)

    async def create_time_log(self, time_log: TimeLogCreate):
        db_time_log = domain_to_orm_timelog_create(time_log)
        self.db.add(db_time_log)
        await self.db.flush()  # Ensure id is generated
        
        # Create a simple domain model without loading the task relationship
        # to avoid the lazy loading issue
        from domain.models.dayplan_model import TimeLog
        return TimeLog(
            id=db_time_log.id,
            task_id=db_time_log.task_id,
            start_time=db_time_log.start_time,
            end_time=db_time_log.end_time,
            plan_id=db_time_log.plan_id,
            done=db_time_log.done,
            task=None  # Don't load the task relationship to avoid lazy loading issues
        )

    async def get_time_log(self, id):
        result = await self.db.execute(select(TimeLog).filter(TimeLog.id == id))
        time_log = result.scalars().first()
        if not time_log:
            return None
        return orm_to_domain_timelog(time_log)
    async def update_time_log(self, time_log_id: int, data: dict) -> dTimeLog:
        """
        Partially update a TimeLog fields with provided kwargs.
        Does NOT commit; flush is optional to get updated id.
        """
        result = await self.db.execute(select(TimeLog).filter(TimeLog.id == time_log_id))
        time_log = result.scalars().first()
        if not time_log:
            return None  # or raise NotFoundError

        # Update only provided fields
        for key, value in data.items():
            if hasattr(time_log, key):
                setattr(time_log, key, value)

        await self.db.flush()  # Optional: ensures changes are applied to the session
        return orm_to_domain_timelog(time_log)


    