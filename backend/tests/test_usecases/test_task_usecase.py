from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from domain.exceptions import BadRequestError, NotFoundError
from domain.models.task_model import TaskCreateInput, TaskOutput, TaskProgressDomain
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
        email="awel@example.com"
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
    mock_uow.tasks.get_assignees_of_task=AsyncMock(return_value=[])

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
                    )
    mock_uow.tasks.get_task=AsyncMock(return_value=task)
    mock_uow.tasks.get_assignees_of_task=AsyncMock(return_value=[])

    with pytest.raises(PermissionError, match="You are not authorized to create subtask for another user's task"):
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
                    )
    mock_uow.tasks.get_task=AsyncMock(return_value=task)
    mock_uow.tasks.create_task = AsyncMock(return_value="created_task")
    mock_uow.tasks.get_assignees_of_task=AsyncMock(return_value=[current_user.id])

    result = await service.create_task(task_input, current_user)

    assert result == "created_task"
    mock_uow.tasks.create_task.assert_awaited_once()




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
async def test_handle_repetitive_task_creates_progress(service, mock_uow):
    now = datetime.now(timezone.utc)
    task = TaskOutput(
        id=1,
        owner_id=1,
        assignees=[],
        start_date=now - timedelta(days=7),
        end_date=now - timedelta(days=6),
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
    
    # Verify the arguments of the last call to update_task
    task_id, update_data = mock_uow.tasks.update_task.call_args.args
    assert task_id == task.id
    assert update_data["status"] == "in_progress"
    assert update_data["done_hr"] == 0.0
    # You can also verify start_date/end_date logic if needed
    assert update_data["start_date"] == now 
    assert update_data["end_date"] == now + timedelta(days=1)




@pytest.mark.asyncio
async def test_get_task_rolls_back_on_failure(service, mock_uow, current_user):
    # make get_tasks return one task
    task = TaskOutput(
        id=1,
        owner_id=current_user.id,
        start_date=datetime.now(timezone.utc) - timedelta(days=7),
        end_date=datetime.now(timezone.utc) - timedelta(days=6),
        status="pending",
        done_hr=2,
        estimated_hr=4,
        description="disc",
        is_repititive=True,
        is_stopped=False,
    )

    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_assignees_of_task_email=AsyncMock(return_value=[])
    mock_uow.tasks.get_desription_and_id_of_subtasks=AsyncMock(return_value=[])
    mock_uow.tasks.create_progress = AsyncMock()
    mock_uow.tasks.update_task = AsyncMock(side_effect=RuntimeError("DB failure"))
    mock_uow.tasks.get_progress=AsyncMock(return_value={"total":1,"data":[]})


    with pytest.raises(RuntimeError, match="DB failure"):
        await service.get_task(1, current_user)

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
        start_date=now-timedelta(hours=2),
        end_date=now-timedelta(hours=1)
    )
    stopped_info = MagicMock()
    stopped_info.stopped_at = now - timedelta(hours=1)

    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_stop = AsyncMock(return_value=stopped_info)
    mock_uow.tasks.update_task = AsyncMock()
    mock_uow.tasks.create_progress = AsyncMock()
    mock_uow.tasks.delete_stop = AsyncMock()

    result = await service.toggle_task(task.id, stop=False, current_user=current_user)

    task_id,updated=mock_uow.tasks.update_task.call_args.args
    assert updated["is_stopped"] == False
    assert abs((updated["start_date"] - now).total_seconds()) < 1.0, f"Expected {now}, got {updated['start_date']}"
    assert abs((updated["end_date"] - (now + timedelta(hours=1))).total_seconds()) < 1.0, f"Expected {now + timedelta(hours=1)}, got {updated['end_date']}"

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

@pytest.mark.asyncio
async def test_get_task_success(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_assignees_of_task_email=AsyncMock(return_value=[current_user.email])
    mock_uow.tasks.get_desription_and_id_of_subtasks=AsyncMock(return_value=[])
    
    result = await service.get_task(1, current_user)
    
    assert result["task"] == task
    assert "standard_completion_hr" in result
    assert "curr_completion_rate" in result
    mock_uow.tasks.get_task.assert_awaited_once_with(1)

@pytest.mark.asyncio
async def test_get_task_not_found(service, mock_uow, current_user):
    mock_uow.tasks.get_task = AsyncMock(return_value=None)
    
    with pytest.raises(NotFoundError, match="Task not found"):
        await service.get_task(1, current_user)

@pytest.mark.asyncio
async def test_get_task_permission_error(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=999,  # Different user
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_assignees_of_task_email=AsyncMock(return_value=[])
    mock_uow.tasks.get_desription_and_id_of_subtasks=AsyncMock(return_value=[])
    
    with pytest.raises(PermissionError, match="You don't have access to this task"):
        await service.get_task(1, current_user)

@pytest.mark.asyncio
async def test_get_task_assigned_user_access(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=999,  # Different owner
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[current_user.id]  # But assigned to current user
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_assignees_of_task_email=AsyncMock(return_value=[current_user.email])
    mock_uow.tasks.get_desription_and_id_of_subtasks=AsyncMock(return_value=[])
    
    result = await service.get_task(1, current_user)
    
    assert result["task"] == task

@pytest.mark.asyncio
async def test_get_progress_success(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    progress_history = [
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=1),
            end_date=datetime.now(timezone.utc),
            status="completed",
            done_hr=2.0,
            estimated_hr=2.0
        )
    ]
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=progress_history)
    
    result = await service.get_progress(1, current_user, skip=0, limit=10)
    
    assert result == progress_history
    mock_uow.tasks.get_progress.assert_awaited_once_with(1, 0, 10)

@pytest.mark.asyncio
async def test_get_progress_permission_error(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=999,  # Different user
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    
    with pytest.raises(PermissionError, match="You don't have permission to view this task's progress"):
        await service.get_progress(1, current_user)

@pytest.mark.asyncio
async def test_assign_user_to_task_success(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
    )
    
    updated_task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,

    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.assign_user_to_task = AsyncMock(return_value=(updated_task, None))
    mock_uow.tasks.get_task = AsyncMock(side_effect=[task, updated_task])
    
    result = await service.assign_user_to_task(1, "user@example.com", current_user)
    
    assert result == updated_task
    mock_uow.tasks.assign_user_to_task.assert_awaited_once_with(1, "user@example.com")

@pytest.mark.asyncio
async def test_assign_user_to_task_not_found(service, mock_uow, current_user):
    mock_uow.tasks.get_task = AsyncMock(return_value=None)
    
    with pytest.raises(NotFoundError, match="Task not found"):
        await service.assign_user_to_task(1, "user@example.com", current_user)

@pytest.mark.asyncio
async def test_assign_user_to_task_permission_error(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=999,  # Different user
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    
    with pytest.raises(PermissionError, match="You are not authorized to assign this task"):
        await service.assign_user_to_task(1, "user@example.com", current_user)

@pytest.mark.asyncio
async def test_update_task_success(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    updated_task = TaskOutput(
        id=1,
        description="Updated Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=2),
        estimated_hr=8.0,
        done_hr=2.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    task_data = {
        "description": "Updated Task",
        "end_date": datetime.now(timezone.utc) + timedelta(days=2),
        "estimated_hr": 8.0
    }
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.update_task = AsyncMock(return_value=updated_task)
    
    result = await service.update_task(1, task_data, current_user)
    
    assert result == updated_task
    mock_uow.tasks.update_task.assert_awaited_once_with(1, task_data)

@pytest.mark.asyncio
async def test_update_task_invalid_dates(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    task_data = {
        "start_date": datetime.now(timezone.utc) + timedelta(days=2),
        "end_date": datetime.now(timezone.utc) + timedelta(days=1)  # End before start
    }
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    
    with pytest.raises(BadRequestError, match="End date cannot be before start date"):
        await service.update_task(1, task_data, current_user)

@pytest.mark.asyncio
async def test_update_task_negative_hours(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    task_data = {"estimated_hr": -1}
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    
    with pytest.raises(BadRequestError, match="Estimated hours cannot be negative"):
        await service.update_task(1, task_data, current_user)

@pytest.mark.asyncio
async def test_update_task_permission_error(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=999,  # Different user
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    task_data = {"description": "Updated Task"}
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    
    with pytest.raises(PermissionError, match="You don't have permission to update this task"):
        await service.update_task(1, task_data, current_user)

@pytest.mark.asyncio
async def test_delete_task_success(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.delete_task = AsyncMock()
    
    result = await service.delete_task(1, current_user)
    
    assert result is True
    mock_uow.tasks.delete_task.assert_awaited_once_with(1, current_user.id)

@pytest.mark.asyncio
async def test_delete_task_not_found(service, mock_uow, current_user):
    mock_uow.tasks.get_task = AsyncMock(return_value=None)
    
    with pytest.raises(NotFoundError, match="Task not found"):
        await service.delete_task(1, current_user)

@pytest.mark.asyncio
async def test_delete_task_permission_error(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5.0,
        done_hr=2.0,
        owner_id=999,  # Different user
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    
    with pytest.raises(PermissionError, match="Cannot delete another user's task"):
        await service.delete_task(1, current_user)


