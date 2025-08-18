# tests/test_dayplan_repository.py
import pytest
from datetime import date, datetime, timedelta

from infrastructure.repositories.dayplan_repository import DayPlanRepository
from infrastructure.models.model import  Task
from domain.models.dayplan_model import  TimeLogCreate
# from infrastructure


@pytest.mark.asyncio
async def test_create_and_get_dayplan(async_session):
    repo = DayPlanRepository(async_session)

    class User:
        id = 1

    # Create
    created = await repo.create_dayplan(date.today(), User())
    assert created.id is not None
    assert created.date == date.today()
    assert created.user_id == 1
    assert created.times == []

    # Fetch
    fetched = await repo.get_dayplan(date.today(), User())
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.user_id == 1
    assert fetched.date == date.today()


@pytest.mark.asyncio
async def test_create_and_delete_dayplan(async_session):
    repo = DayPlanRepository(async_session)

    class User:
        id = 1

    created = await repo.create_dayplan(date.today(), User())
    assert created is not None

    deleted = await repo.delete_dayplan(date.today(), User())
    assert deleted is not None
    assert deleted.id == created.id

    # Verify deletion
    fetched = await repo.get_dayplan(date.today(), User())
    assert fetched is None


@pytest.mark.asyncio
async def test_create_get_update_delete_timelog(async_session):
    repo = DayPlanRepository(async_session)

    class User:
        id = 1

    # Must create a DayPlan first
    dayplan = await repo.create_dayplan(date.today(), User())

    # Must create a Task because TimeLog.task_id is mandatory
    task = Task(
        description="Test task",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=1),
        estimated_hr=5,
        owner_id=User.id,
    )
    async_session.add(task)
    await async_session.flush()   # ensures task.id is generated

    # Domain timelog
    timelog = TimeLogCreate(
        start_time=datetime.now().time(),
        end_time=(datetime.now() + timedelta(hours=1)).time(),
        task_id=task.id,   # ✅ use real task id
        plan_id=dayplan.id
    )

    created = await repo.create_time_log(timelog)
    assert created.id is not None
    assert created.task_id == task.id
    assert created.plan_id == dayplan.id

    # Fetched
    fetched = await repo.get_time_log(created.id)
    assert fetched is not None
    assert fetched.id == created.id

    # Update
    updated = await repo.update_time_log(created.id, {"task_id": task.id})
    assert updated.task_id == task.id

    # Delete
    deleted = await repo.deleteTimeLog(created.id)
    assert deleted.id == created.id

    # Verify gone
    missing = await repo.get_time_log(created.id)
    assert missing is None
