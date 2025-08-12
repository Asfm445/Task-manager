from datetime import date

from domain.models.dayplan_model import TimeLog as dTimeLog
from domain.repositories.dayplan_repo import AbstractDayPlanRepository
from infrastructure.dto.dayplan_dto import (
    domain_to_orm_timelog,
    orm_to_domain_dayplan,
    orm_to_domain_timelog,
)
from infrastructure.models.model import DayPlan, TimeLog
from sqlalchemy.orm import Session


class DayPlanRepository(AbstractDayPlanRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_dayplan(self, date: date, current_user) -> DayPlan:
        dayplan = DayPlan(date=date, user_id=current_user.id)
        self.db.add(dayplan)
        self.db.commit()
        self.db.refresh(dayplan)
        return orm_to_domain_dayplan(dayplan)

    def get_dayplan(self, date: date, current_user) -> DayPlan:
        result = (
            self.db.query(DayPlan)
            .filter(DayPlan.date == date, DayPlan.user_id == current_user.id)
            .first()
        )
        if not result:
            return None
        return orm_to_domain_dayplan(result)

    def get_dayplanById(self, id: int) -> DayPlan:
        result = self.db.query(DayPlan).filter(DayPlan.id == id).first()
        if not result:
            return None
        return orm_to_domain_dayplan(result)

    def delete_dayplan(self, date: date, current_user) -> DayPlan:
        dayplan = self.get_dayplan(date, current_user)
        self.db.delete(dayplan)
        self.db.commit()
        return orm_to_domain_dayplan(dayplan)

    def deleteTimeLog(self, id):
        time_log = self.db.query(TimeLog).filter(TimeLog.id == id).first()
        if not time_log:
            return None
        self.db.delete(time_log)
        self.db.commit()
        return orm_to_domain_timelog(time_log)

    def create_time_log(self, time_log: dTimeLog):
        db_time_log = domain_to_orm_timelog(time_log)
        self.db.add(db_time_log)
        self.db.commit()
        self.db.refresh(db_time_log)
        return orm_to_domain_timelog(db_time_log)

    def get_time_log(self, id):
        time_log = self.db.query(TimeLog).filter(TimeLog.id == id).first()
        if not time_log:
            return None
        return orm_to_domain_timelog(time_log)
