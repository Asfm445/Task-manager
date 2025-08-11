from datetime import date

from infrastructure.models.model import DayPlan, TimeLog
from sqlalchemy.orm import Session


class DayPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_dayplan(self, date: date, current_user) -> DayPlan:
        dayplan = DayPlan(date=date, user_id=current_user.id)
        self.db.add(dayplan)
        self.db.commit()
        self.db.refresh(dayplan)
        return dayplan

    def get_dayplan(self, date: date, current_user) -> DayPlan:
        return (
            self.db.query(DayPlan)
            .filter(DayPlan.date == date, DayPlan.user_id == current_user.id)
            .first()
        )

    def delete_dayplan(self, date: date, current_user) -> DayPlan:
        dayplan = self.get_dayplan(date, current_user)
        self.db.delete(dayplan)
        self.db.commit()
        return dayplan

    def deleteTimeLog(self, id):
        time_log = self.db.query(TimeLog).filter(TimeLog.id == id).first()
        if not time_log:
            return None
        self.db.delete(time_log)
        self.db.commit()
        return time_log

    def create_time_log(self, time_log: dict):
        db_time_log = TimeLog(**time_log)
        self.db.add(db_time_log)
        self.db.commit()
        self.db.refresh(db_time_log)
        return db_time_log
