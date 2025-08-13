# schema to domain converter for DayPlanCreate → DayPlan
from api.schemas.dayplan_schema import DayPlanCreate, TimeCreate
from domain.models.dayplan_model import DayPlan, TimeLogCreate


def dayplan_create_to_domain(schema: DayPlanCreate, user_id: int) -> DayPlan:
    return DayPlan(
        id=None,  # Not set yet, will be assigned by DB
        date=schema.date,
        user_id=user_id,
        times=[],
    )


# schema to domain converter for TimeCreate → TimeLogCreate
def time_create_to_domain(schema: TimeCreate) -> TimeLogCreate:
    return TimeLogCreate(
        task_id=schema.task_id,
        start_time=schema.start_time,
        end_time=schema.end_time,
        plan_id=schema.plan_id,
    )

#updated changeed
