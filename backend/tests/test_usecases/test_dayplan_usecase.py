# tests/unit/test_dayplan_usecase.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date, datetime, time, timedelta

from domain.models.dayplan_model import TimeLogCreate
from domain.exceptions import NotFoundError, BadRequestError
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


