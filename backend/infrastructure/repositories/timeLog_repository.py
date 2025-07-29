from models.model import TimeLog
from sqlalchemy.orm import Session


class TimeLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_time_logs(self, plan_id: int, user_email: str):
        return (
            self.db.query(TimeLog)
            .filter(TimeLog.plan_id == plan_id, TimeLog.task.owner.email == user_email)
            .all()
        )

    def create_time_log(self, time_log: dict):
        db_time_log = TimeLog(**time_log)
        self.db.add(db_time_log)
        self.db.commit()
        self.db.refresh(db_time_log)
        return db_time_log

    def delete_time_log(self, time_log_id: int):
        time_log = self.db.query(TimeLog).filter(TimeLog.id == time_log_id).first()
        if not time_log:
            return False
        self.db.delete(time_log)
        self.db.commit()
        return True
