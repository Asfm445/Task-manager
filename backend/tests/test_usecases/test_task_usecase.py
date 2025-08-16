import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta

from domain.exceptions import BadRequestError, NotFoundError
from domain.models.task_model import TaskCreateInput, TaskOutput
from usecases.task_usecase import TaskService


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = False
    uow.tasks = MagicMock()
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    return uow


@pytest.fixture
def service(mock_uow):
    return TaskService(mock_uow)


@pytest.fixture
def current_user():
    class User:
        id = 1
    return User()


@pytest.mark.asyncio
async def test_create_task_success(service, mock_uow, current_user):
    task_input = TaskCreateInput(
        # title="Test",
        description="desc",
        start_date=datetime.now(timezone.utc) + timedelta(days=1),
        end_date=datetime.now(timezone.utc) + timedelta(days=2),
        estimated_hr=5,
        is_repititive=False
    )
    mock_uow.tasks.create_task = AsyncMock(return_value="created_task")

    result = await service.create_task(task_input, current_user)

    assert result == "created_task"
    mock_uow.tasks.create_task.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_task_start_date_before_end_date(service,current_user):
    task_input = TaskCreateInput(
        # title="Test",
        description="desc",
        start_date=datetime.now(timezone.utc) + timedelta(days=2),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5,
        is_repititive=False
    )
    with pytest.raises(BadRequestError, match="End date cannot be before start date"):
        await service.create_task(task_input, current_user)

@pytest.mark.asyncio
async def test_validate_date_end_date_before__start_date(service):
    start_date=datetime.now(timezone.utc) + timedelta(days=2)
    end_date=datetime.now(timezone.utc) + timedelta(days=1)
    with pytest.raises(BadRequestError, match="End date cannot be before start date"):
        await service._validate_dates(start_date, end_date)

@pytest.mark.asyncio
async def test_validate_date_start_date_is_past(service):
    start_date=datetime.now(timezone.utc) - timedelta(days=2)
    end_date=datetime.now(timezone.utc) - timedelta(days=1)
    with pytest.raises(BadRequestError, match="Start date cannot be in the past"):
        await service._validate_dates(start_date, end_date)






@pytest.mark.asyncio
async def test_create_task_negative_hours(service, current_user):
    task_input = TaskCreateInput(
        # title="Test",
        description="desc",
        start_date=datetime.now(timezone.utc) + timedelta(days=1),
        end_date=datetime.now(timezone.utc) + timedelta(days=2),
        estimated_hr=-1,
        is_repititive=False
    )

    with pytest.raises(BadRequestError):
        await service.create_task(task_input, current_user)


@pytest.mark.asyncio
async def test_create_subtask_main_task_notfound(service, mock_uow, current_user):
    task_input = TaskCreateInput(
        # title="Test",
        main_task_id=1,
        description="desc",
        start_date=datetime.now(timezone.utc) + timedelta(days=1),
        end_date=datetime.now(timezone.utc) + timedelta(days=2),
        estimated_hr=11,
        is_repititive=False
    )
    mock_uow.tasks.get_task=AsyncMock(return_value=None)

    with pytest.raises(NotFoundError, match="Main task not found"):
        await service.create_task(task_input, current_user)

@pytest.mark.asyncio
async def test_create_subtask_has_no_pernmission(service, mock_uow, current_user):
    task_input = TaskCreateInput(
        # title="Test",
        main_task_id=1,
        description="desc",
        start_date=datetime.now(timezone.utc) + timedelta(days=1),
        end_date=datetime.now(timezone.utc) + timedelta(days=2),
        estimated_hr=1,
        is_repititive=False
    )
    task = TaskOutput(id=1,
                      description="disc",
                      end_date=datetime.now(timezone.utc) + timedelta(days=2),
                      estimated_hr=1,
                      owner_id=99, 
                      assignees=[])
    mock_uow.tasks.get_task=AsyncMock(return_value=task)

    with pytest.raises(PermissionError, match="Cannot create subtask for another user's task"):
        await service.create_task(task_input, current_user)

@pytest.mark.asyncio
async def test_assigned_user_create_subtask(service, mock_uow, current_user):
    task_input = TaskCreateInput(
        # title="Test",
        main_task_id=1,
        description="desc",
        start_date=datetime.now(timezone.utc) + timedelta(days=1),
        end_date=datetime.now(timezone.utc) + timedelta(days=2),
        estimated_hr=1,
        is_repititive=False
    )
    task = TaskOutput(id=1,
                      description="disc",
                      end_date=datetime.now(timezone.utc) + timedelta(days=2),
                      estimated_hr=1,
                      owner_id=99, 
                      assignees=[1])
    mock_uow.tasks.get_task=AsyncMock(return_value=task)
    mock_uow.tasks.create_task = AsyncMock(return_value="created_task")

    result = await service.create_task(task_input, current_user)

    assert result == "created_task"
    mock_uow.tasks.create_task.assert_awaited_once()



@pytest.mark.asyncio
async def test_delete_task_permission_error(service, mock_uow, current_user):
    task = TaskOutput(id=1,
                      description="disc",
                      end_date=datetime.now(timezone.utc) + timedelta(days=2),
                      estimated_hr=1,
                      owner_id=99, 
                      assignees=[])
    mock_uow.tasks.get_task = AsyncMock(return_value=task)

    with pytest.raises(PermissionError):
        await service.delete_task(1, current_user)

    mock_uow.tasks.delete_task.assert_not_called()


@pytest.mark.asyncio
async def test_update_task(service, mock_uow, current_user):
    """
    Ensures that if an exception is raised during update, the transaction is rolled back.
    """
    task = TaskOutput(id=1,
                      description="disc",
                      end_date=datetime.now(timezone.utc) + timedelta(days=2),
                      estimated_hr=1,
                      owner_id=1, 
                      assignees=[])
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.update_task = AsyncMock(side_effect=RuntimeError("DB failure"))

    with pytest.raises(RuntimeError):
        await service.update_task(1, {"estimated_hr": 5}, current_user)



@pytest.mark.asyncio
async def test_get_tasks_filters_by_user(service, mock_uow, current_user):
    task_owned = TaskOutput(id=1,
                      description="disc",
                      end_date=datetime.now(timezone.utc) + timedelta(days=2),
                      estimated_hr=1,
                      owner_id=current_user.id, 
                      assignees=[])
    task_assigned = TaskOutput(id=1,
                      description="disc",
                      end_date=datetime.now(timezone.utc) + timedelta(days=2),
                      estimated_hr=1,
                      owner_id=1, 
                      assignees=[1])
    task_unrelated = TaskOutput(id=1,
                      description="disc",
                      end_date=datetime.now(timezone.utc) + timedelta(days=2),
                      estimated_hr=1,
                      owner_id=2, 
                      assignees=[])

    mock_uow.tasks.get_tasks = AsyncMock(return_value=[task_owned, task_assigned, task_unrelated])

    result = await service.get_tasks(current_user)

    assert len(result) == 2
    assert all(t in [task_owned, task_assigned] for t in result)
    mock_uow.commit.assert_awaited()


@pytest.mark.asyncio
async def test_handle_repetitive_task_creates_progress(service, mock_uow):
    task = TaskOutput(
        id=1,
        owner_id=1,
        assignees=[],
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now() - timedelta(days=6),
        status="pending",
        done_hr=2,
        estimated_hr=4,
        description="disc",
        is_repititive=True,
        is_stopped=False
    )

    mock_uow.tasks.create_progress = AsyncMock()
    mock_uow.tasks.update_task = AsyncMock()

    await service._handle_repetitive_task(task)

    assert mock_uow.tasks.create_progress.await_count == 7
    mock_uow.tasks.update_task.assert_awaited()




@pytest.mark.asyncio
async def test_get_tasks_rolls_back_on_failure(service, mock_uow, current_user):
    # make get_tasks return one task
    task = TaskOutput(
        id=1,
        owner_id=current_user.id,
        assignees=[],
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now() - timedelta(days=6),
        status="pending",
        done_hr=2,
        estimated_hr=4,
        description="disc",
        is_repititive=True,
        is_stopped=False,
    )

    mock_uow.tasks.get_tasks = AsyncMock(return_value=[task])
    mock_uow.tasks.create_progress = AsyncMock()
    mock_uow.tasks.update_task = AsyncMock(side_effect=RuntimeError("DB failure"))


    with pytest.raises(RuntimeError, match="DB failure"):
        await service.get_tasks(skip=0, limit=10, current_user=current_user)

    mock_uow.commit.assert_not_awaited()
    mock_uow.rollback.assert_awaited()

    # mock_uow.tasks.create_progress.assert_not_awaited()


@pytest.mark.asyncio
async def test_toggle_task_stop_success(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        owner_id=current_user.id,
        assignees=[],
        is_repititive=True,
        is_stopped=False,
        description="desc",
        estimated_hr=1,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc)
    )
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.update_task = AsyncMock()
    mock_uow.tasks.create_stop = AsyncMock()

    result = await service.toggle_task(task.id, stop=True, current_user=current_user)

    assert result == {"message": "task stopped successfully"}
    mock_uow.tasks.update_task.assert_awaited_once_with(task.id, {"is_stopped": True})
    mock_uow.tasks.create_stop.assert_awaited_once()
    mock_uow.commit.assert_awaited()

@pytest.mark.asyncio
async def test_toggle_task_start_success(service, mock_uow, current_user):
    now = datetime.now(timezone.utc)
    task = TaskOutput(
        id=1,
        owner_id=current_user.id,
        assignees=[],
        is_repititive=True,
        is_stopped=True,
        description="desc",
        estimated_hr=1,
        start_date=now,
        end_date=now
    )
    stopped_info = MagicMock()
    stopped_info.stopped_at = now - timedelta(hours=1)

    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_stop = AsyncMock(return_value=stopped_info)
    mock_uow.tasks.update_task = AsyncMock()
    mock_uow.tasks.create_progress = AsyncMock()
    mock_uow.tasks.delete_stop = AsyncMock()

    result = await service.toggle_task(task.id, stop=False, current_user=current_user)

    assert result == {"message": "task started successfully"}
    mock_uow.tasks.update_task.assert_awaited_once()
    mock_uow.tasks.create_progress.assert_awaited_once()
    mock_uow.tasks.delete_stop.assert_awaited_once()
    mock_uow.commit.assert_awaited()

@pytest.mark.asyncio
async def test_toggle_task_update_fails_triggers_exception(service, mock_uow, current_user):
    """
    Ensure that if update_task fails, toggle_task raises an exception and no partial state happens.
    """
    task = TaskOutput(
        id=1,
        owner_id=current_user.id,
        assignees=[],
        is_repititive=True,
        is_stopped=False,
        description="desc",
        estimated_hr=1,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc)
    )

    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    # Simulate DB failure
    mock_uow.tasks.update_task = AsyncMock(side_effect=RuntimeError("DB failure"))
    mock_uow.tasks.create_stop = AsyncMock()

    with pytest.raises(RuntimeError, match="DB failure"):
        await service.toggle_task(task.id, stop=True, current_user=current_user)

    # Ensure create_stop was never called (atomicity)
    mock_uow.tasks.create_stop.assert_not_awaited()
    mock_uow.commit.assert_not_awaited()
    mock_uow.rollback.assert_awaited()
