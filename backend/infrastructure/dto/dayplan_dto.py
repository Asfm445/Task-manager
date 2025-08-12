from domain.models.dayplan_model import DayPlan, TimeLog
from infrastructure.models.model import DayPlan as dbDayplan
from infrastructure.models.model import TimeLog as dbTimelog


def orm_to_domain_dayplan(orm_dayplan: dbDayplan) -> DayPlan:
    return DayPlan(
        id=orm_dayplan.id,
        date=orm_dayplan.date,
        user_id=orm_dayplan.user_id,
        times=[orm_to_domain_timelog(t) for t in orm_dayplan.times],
    )


def orm_to_domain_timelog(orm_timelog: dbTimelog) -> TimeLog:
    return TimeLog(
        id=orm_timelog.id,
        task_id=orm_timelog.task_id,
        start_time=orm_timelog.start_time,
        end_time=orm_timelog.end_time,
        plan_id=orm_timelog.plan_id,
        task=orm_timelog.task,
    )


def domain_to_orm_dayplan(domain_dayplan: DayPlan, orm_dayplan=None):
    if orm_dayplan is None:
        orm_dayplan = dbDayplan()  # Your SQLAlchemy ORM model class
    orm_dayplan.date = domain_dayplan.date
    orm_dayplan.user_id = domain_dayplan.user_id
    # Handle times if needed separately
    return orm_dayplan


def domain_to_orm_timelog(domain_timelog: TimeLog, orm_timelog=None):
    if orm_timelog is None:
        orm_timelog = dbTimelog()
    orm_timelog.task_id = domain_timelog.task_id
    orm_timelog.start_time = domain_timelog.start_time
    orm_timelog.end_time = domain_timelog.end_time
    orm_timelog.plan_id = domain_timelog.plan_id
    return orm_timelog
