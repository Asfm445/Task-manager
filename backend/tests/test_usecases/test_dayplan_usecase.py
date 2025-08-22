# tests/unit/test_dayplan_usecase.py
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from domain.exceptions import BadRequestError, NotFoundError
from domain.models.dayplan_model import TimeLogCreate
from usecases.dayplan_usecase import DayPlanUseCase


class FakeUser:
    id = 1

@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = False
    uow.dayplan_repo = MagicMock()
    uow.task_repo = MagicMock()
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    return uow

@pytest.mark.asyncio
async def test_get_dayplan_creates_if_not_exists(mock_uow):
    # Mock UoW and repository
    dayplan_repo = AsyncMock()
    dayplan_repo.get_dayplan.return_value = None
    dayplan_repo.create_dayplan.return_value = "new_dayplan"

    mock_uow.dayplan_repo = dayplan_repo
    usecase = DayPlanUseCase(mock_uow)

    result = await usecase.get_dayplan(date.today(), FakeUser())

    dayplan_repo.create_dayplan.assert_awaited_once()
    assert result == "new_dayplan"

@pytest.mark.asyncio
async def test_delete_dayplan_not_found(mock_uow):
    dayplan_repo = AsyncMock()
    dayplan_repo.get_dayplan.return_value = None


    mock_uow.dayplan_repo = dayplan_repo
    usecase = DayPlanUseCase(mock_uow)

    with pytest.raises(NotFoundError):
        await usecase.delete_dayplan(date.today(), FakeUser())

@pytest.mark.asyncio
async def test_create_time_log_overlaps(mock_uow):

    class FakeUser:
        id = 1

    # Existing timelog that overlaps
    now = datetime.now()
    existing_timelog = MagicMock()
    existing_timelog.start_time = now
    existing_timelog.end_time = now + timedelta(hours=1)

    dayplan_repo = AsyncMock()
    dayplan_repo.get_dayplanById.return_value = MagicMock(times=[existing_timelog])
    
    task = MagicMock()
    task.owner_id = 1
    task.status = "in_progress"
    task.id = 1

    task_repo = AsyncMock()
    task_repo.get_task.return_value = task

    
    mock_uow.dayplan_repo = dayplan_repo
    mock_uow.task_repo = task_repo

    usecase = DayPlanUseCase(mock_uow)

    new_timelog = TimeLogCreate(
        start_time=now + timedelta(minutes=30),   # Overlaps with existing
        end_time=now + timedelta(hours=1, minutes=30),
        task_id=1,
        plan_id=1
    )

    with pytest.raises(BadRequestError):
        await usecase.create_time_log(new_timelog, FakeUser())

@pytest.mark.asyncio
async def test_mark_timelog_success_updates_done_hr(mock_uow):
    # Setup task and timelog
    task = MagicMock()
    task.owner_id = 1
    task.estimated_hr = 1
    task.done_hr = 0
    task.status = "in_progress"
    task.main_task_id=None

    up_task = MagicMock()
    up_task.owner_id = 1
    up_task.estimated_hr = 1
    up_task.done_hr = 1
    up_task.status = "in_progress"
    up_task.main_task_id=None

    timelog = MagicMock()
    timelog.id = 1
    timelog.start_time = (datetime.now() - timedelta(hours=1)).time()
    timelog.end_time = datetime.now().time()
    timelog.task = task
    timelog.done = False

    up_timelog = MagicMock()
    up_timelog.id = 1
    up_timelog.start_time = (datetime.now() - timedelta(hours=1)).time()
    up_timelog.end_time = datetime.now().time()
    up_timelog.task = task
    up_timelog.done = True

    dayplan_repo = AsyncMock()
    dayplan_repo.get_time_log.return_value = timelog
    dayplan_repo.update_time_log.return_value = up_timelog

    task_repo = AsyncMock()
    task_repo.get_task.return_value = task
    task_repo.update_task.return_value = up_task


    mock_uow.dayplan_repo = dayplan_repo
    mock_uow.task_repo = task_repo

    usecase = DayPlanUseCase(mock_uow)

    result = await usecase.mark_timelog_success(1, FakeUser())

    assert result.done == True
    assert result.task.done_hr==1
    mock_uow.task_repo.update_task.assert_awaited()
    assert mock_uow.task_repo.update_task.await_count==1
    mock_uow.commit.assert_awaited()


@pytest.mark.asyncio
async def test_timelog_completion_propagates_to_parent(mock_uow):
    usecase = DayPlanUseCase(mock_uow)

    # Fake timelog with a child task
    child_task = MagicMock()
    child_task.id = 1
    child_task.owner_id = 1
    child_task.done_hr = 5
    child_task.estimated_hr = 5  # Already meets completion
    child_task.status = "pending"
    child_task.main_task_id = 2  # parent exists

    parent_task = MagicMock()
    parent_task.id = 2
    parent_task.owner_id = 1
    parent_task.done_hr = 0
    parent_task.estimated_hr = 10
    parent_task.status = "pending"
    parent_task.main_task_id = None

    timelog = MagicMock()
    timelog.id = 1
    timelog.start_time = (datetime.now() - timedelta(hours=1)).time()
    timelog.end_time = datetime.now().time()
    timelog.task = child_task
    timelog.done = False

    up_timelog = MagicMock()
    up_timelog.id = 1
    up_timelog.start_time = (datetime.now() - timedelta(hours=1)).time()
    up_timelog.end_time = datetime.now().time()
    up_timelog.task = child_task
    up_timelog.done = True

    # Mock repo behavior
    mock_uow.dayplan_repo.get_time_log = AsyncMock(return_value=timelog)
    mock_uow.dayplan_repo.update_time_log = AsyncMock(return_value=timelog)

    # child gets updated to completed
    mock_uow.task_repo.update_task = AsyncMock(side_effect=[
        child_task,
        parent_task
    ])

    mock_uow.task_repo.get_task = AsyncMock(return_value=parent_task)


    # Act
    result = await usecase.mark_timelog_success(timelog.id, FakeUser)

    # Assert
    assert result == timelog
    # First update: child task completed
    mock_uow.task_repo.update_task.assert_any_call(
        child_task.id, {"done_hr": child_task.done_hr, "status": "completed"}
    )
    # Then parent got updated
    mock_uow.task_repo.update_task.assert_any_call(
        parent_task.id, {"done_hr": parent_task.done_hr, "status": "in_progress"}
    )
    mock_uow.task_repo.get_task.assert_called_once_with(parent_task.id)





@pytest.mark.asyncio
async def test_mark_timelog_success_done_already(mock_uow):
    # Setup task and timelog
    task = MagicMock()
    task.owner_id = 1
    task.estimated_hr = 1
    task.done_hr = 0
    task.status = "in_progress"
    task.main_task_id=None

    timelog = MagicMock()
    timelog.id = 1
    timelog.start_time = (datetime.now() - timedelta(hours=1)).time()
    timelog.end_time = datetime.now().time()
    timelog.task = task
    timelog.done = True

    dayplan_repo = AsyncMock()
    dayplan_repo.get_time_log.return_value = timelog

    task_repo = AsyncMock()

    mock_uow.dayplan_repo = dayplan_repo
    mock_uow.task_repo = task_repo

    usecase = DayPlanUseCase(mock_uow)

    with pytest.raises(BadRequestError, match="time log already done"):
        await usecase.mark_timelog_success(timelog.id, FakeUser())
    
    mock_uow.rollback.assert_awaited()


    # result = await usecase.mark_timelog_success(1, FakeUser())

    # assert result.done == False
    # task_repo.update_task.assert_awaited()


@pytest.mark.asyncio
async def test_mark_timelog_success_task_update_failed(mock_uow):
    # Setup task and timelog
    task = MagicMock()
    task.owner_id = 1
    task.estimated_hr = 1
    task.done_hr = 0
    task.status = "in_progress"
    task.main_task_id=None

    timelog = MagicMock()
    timelog.id = 1
    timelog.start_time = (datetime.now() - timedelta(hours=1)).time()
    timelog.end_time = datetime.now().time()
    timelog.task = task
    timelog.done = False

    up_timelog = MagicMock()
    up_timelog.id = 1
    up_timelog.start_time = (datetime.now() - timedelta(hours=1)).time()
    up_timelog.end_time = datetime.now().time()
    up_timelog.task = task
    up_timelog.done = True

    dayplan_repo = AsyncMock()
    dayplan_repo.get_time_log.return_value = timelog
    dayplan_repo.update_time_log.return_value = up_timelog

    task_repo = AsyncMock()
    task_repo.get_task.return_value = task
    task_repo.update_task = AsyncMock(side_effect=RuntimeError("DB failure"))


    mock_uow.dayplan_repo = dayplan_repo
    mock_uow.task_repo = task_repo

    usecase = DayPlanUseCase(mock_uow)

    with pytest.raises(RuntimeError, match="DB failure"):
        await usecase.mark_timelog_success(timelog.id, FakeUser())


    
    mock_uow.commit.assert_not_awaited()
    mock_uow.rollback.assert_awaited()

# --------------------- Additional DayPlan coverage ---------------------

@pytest.mark.asyncio
async def test_get_dayplan_returns_existing(mock_uow):
    dayplan_repo = AsyncMock()
    dayplan_repo.get_dayplan.return_value = "existing_dayplan"
    mock_uow.dayplan_repo = dayplan_repo
    usecase = DayPlanUseCase(mock_uow)

    result = await usecase.get_dayplan(date.today(), FakeUser())

    dayplan_repo.get_dayplan.assert_awaited_once()
    assert result == "existing_dayplan"

@pytest.mark.asyncio
async def test_delete_dayplan_success(mock_uow):
    dayplan_repo = AsyncMock()
    dayplan_repo.get_dayplan.return_value = "existing_dayplan"
    dayplan_repo.delete_dayplan.return_value = "deleted_dayplan"
    mock_uow.dayplan_repo = dayplan_repo

    usecase = DayPlanUseCase(mock_uow)
    result = await usecase.delete_dayplan(date.today(), FakeUser())

    dayplan_repo.delete_dayplan.assert_awaited_once()
    assert result == "deleted_dayplan"

@pytest.mark.asyncio
async def test_create_time_log_start_after_end_raises(mock_uow):
    now = datetime.now()
    # Minimal repos to pass earlier checks if reached
    mock_uow.dayplan_repo = AsyncMock()
    mock_uow.task_repo = AsyncMock()
    mock_uow.dayplan_repo.get_dayplanById.return_value = MagicMock(times=[])
    mock_uow.task_repo.get_task.return_value = MagicMock(owner_id=1, status="in_progress", id=1)

    usecase = DayPlanUseCase(mock_uow)

    new_timelog = TimeLogCreate(
        start_time=now + timedelta(hours=2),
        end_time=now + timedelta(hours=1),  # start after end
        task_id=1,
        plan_id=1,
    )

    with pytest.raises(BadRequestError, match="Start time must be before end time"):
        await usecase.create_time_log(new_timelog, FakeUser())

@pytest.mark.asyncio
async def test_create_time_log_dayplan_not_found(mock_uow):
    now = datetime.now()
    mock_uow.dayplan_repo = AsyncMock()
    mock_uow.task_repo = AsyncMock()
    mock_uow.dayplan_repo.get_dayplanById.return_value = None

    usecase = DayPlanUseCase(mock_uow)

    new_timelog = TimeLogCreate(
        start_time=now,
        end_time=now + timedelta(hours=1),
        task_id=1,
        plan_id=1,
    )

    with pytest.raises(NotFoundError, match="DayPlan not found"):
        await usecase.create_time_log(new_timelog, FakeUser())

@pytest.mark.asyncio
async def test_create_time_log_task_not_found(mock_uow):
    now = datetime.now()
    mock_uow.dayplan_repo = AsyncMock()
    mock_uow.task_repo = AsyncMock()
    mock_uow.dayplan_repo.get_dayplanById.return_value = MagicMock(times=[])
    mock_uow.task_repo.get_task.return_value = None

    usecase = DayPlanUseCase(mock_uow)

    new_timelog = TimeLogCreate(
        start_time=now,
        end_time=now + timedelta(hours=1),
        task_id=99,
        plan_id=1,
    )

    with pytest.raises(NotFoundError, match="Task not found"):
        await usecase.create_time_log(new_timelog, FakeUser())

@pytest.mark.asyncio
async def test_create_time_log_permission_denied(mock_uow):
    now = datetime.now()
    mock_uow.dayplan_repo = AsyncMock()
    mock_uow.task_repo = AsyncMock()
    mock_uow.dayplan_repo.get_dayplanById.return_value = MagicMock(times=[])
    # Task owned by someone else
    mock_uow.task_repo.get_task.return_value = MagicMock(owner_id=2, status="pending", id=1)

    usecase = DayPlanUseCase(mock_uow)

    new_timelog = TimeLogCreate(
        start_time=now,
        end_time=now + timedelta(hours=1),
        task_id=1,
        plan_id=1,
    )

    with pytest.raises(PermissionError, match="You don't have permission to work on this task"):
        await usecase.create_time_log(new_timelog, FakeUser())

@pytest.mark.asyncio
async def test_create_time_log_success_updates_task_if_pending(mock_uow):
    now = datetime.now()
    dayplan_repo = AsyncMock()
    task_repo = AsyncMock()
    dayplan_repo.get_dayplanById.return_value = MagicMock(times=[])

    # Task is pending initially
    task = MagicMock(id=1, owner_id=1, status="pending")
    task_repo.get_task.return_value = task
    task_repo.update_task = AsyncMock(return_value=MagicMock(id=1, owner_id=1, status="in_progress"))

    created_timelog = MagicMock()
    dayplan_repo.create_time_log.return_value = created_timelog

    mock_uow.dayplan_repo = dayplan_repo
    mock_uow.task_repo = task_repo

    usecase = DayPlanUseCase(mock_uow)

    new_timelog = TimeLogCreate(
        start_time=now,
        end_time=now + timedelta(hours=1),
        task_id=1,
        plan_id=1,
    )

    result = await usecase.create_time_log(new_timelog, FakeUser())

    task_repo.update_task.assert_awaited_once_with(1, {"status": "in_progress"})
    dayplan_repo.create_time_log.assert_awaited_once_with(new_timelog)
    mock_uow.commit.assert_awaited()
    assert result == created_timelog

@pytest.mark.asyncio
async def test_delete_timelog_not_found(mock_uow):
    dayplan_repo = AsyncMock()
    dayplan_repo.get_time_log.return_value = None
    mock_uow.dayplan_repo = dayplan_repo

    usecase = DayPlanUseCase(mock_uow)

    with pytest.raises(NotFoundError, match="Time log not found"):
        await usecase.delete_timelog(1, FakeUser())

@pytest.mark.asyncio
async def test_delete_timelog_permission_denied(mock_uow):
    # timelog exists but owned by another user
    other_task = MagicMock(owner_id=2)
    timelog = MagicMock(task=other_task)

    dayplan_repo = AsyncMock()
    dayplan_repo.get_time_log.return_value = timelog
    mock_uow.dayplan_repo = dayplan_repo

    usecase = DayPlanUseCase(mock_uow)

    with pytest.raises(PermissionError, match="You don't have permission to delete this time log"):
        await usecase.delete_timelog(1, FakeUser())

@pytest.mark.asyncio
async def test_delete_timelog_success(mock_uow):
    my_task = MagicMock(owner_id=1)
    timelog = MagicMock(task=my_task)

    dayplan_repo = AsyncMock()
    dayplan_repo.get_time_log.return_value = timelog
    dayplan_repo.deleteTimeLog.return_value = "deleted"
    mock_uow.dayplan_repo = dayplan_repo

    usecase = DayPlanUseCase(mock_uow)

    result = await usecase.delete_timelog(1, FakeUser())

    dayplan_repo.deleteTimeLog.assert_awaited_once_with(1)
    assert result == "deleted"




