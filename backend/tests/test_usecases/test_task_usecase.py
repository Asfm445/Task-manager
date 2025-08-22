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


@pytest.mark.asyncio
async def test_get_task_analytics_success(service, mock_uow, current_user):
    # Mock task data
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=5),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=10.0,
        done_hr=6.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=True,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    # Mock progress history
    progress_history = [
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=4),
            end_date=datetime.now(timezone.utc) - timedelta(days=3),
            status="completed",
            done_hr=3.0,
            estimated_hr=3.0
        ),
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=2),
            end_date=datetime.now(timezone.utc) - timedelta(days=1),
            status="completed",
            done_hr=3.0,
            estimated_hr=3.0
        )
    ]
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=progress_history)
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    
    assert "task" in result
    assert "analytics" in result
    assert result["task"] == task
    
    analytics = result["analytics"]
    assert "completion_metrics" in analytics
    assert "time_efficiency" in analytics
    assert "progress_trends" in analytics
    assert "performance_indicators" in analytics
    assert "status_analysis" in analytics
    assert "time_analysis" in analytics
    assert "summary" in analytics

@pytest.mark.asyncio
async def test_get_task_analytics_completion_metrics(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=5),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=10.0,
        done_hr=6.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=[])
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    completion_metrics = result["analytics"]["completion_metrics"]
    
    assert completion_metrics["completion_rate"] == 60.0  # 6/10 * 100
    assert completion_metrics["remaining_hours"] == 4.0   # 10 - 6
    assert completion_metrics["done_hours"] == 6.0
    assert completion_metrics["estimated_hours"] == 10.0
    assert completion_metrics["progress_percentage"] == 60.0

@pytest.mark.asyncio
async def test_get_task_analytics_time_efficiency(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=5),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=10.0,
        done_hr=6.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=True,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    progress_history = [
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=4),
            end_date=datetime.now(timezone.utc) - timedelta(days=3),
            status="completed",
            done_hr=3.0,
            estimated_hr=3.0
        ),
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=2),
            end_date=datetime.now(timezone.utc) - timedelta(days=1),
            status="completed",
            done_hr=3.0,
            estimated_hr=3.0
        )
    ]
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=progress_history)
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    time_efficiency = result["analytics"]["time_efficiency"]
    
    assert time_efficiency["cycles_completed"] == 2
    assert time_efficiency["total_cycles"] == 2
    assert time_efficiency["avg_hours_per_cycle"] == 3.0  # (3+3)/2
    assert time_efficiency["total_hours_worked"] == 6.0

@pytest.mark.asyncio
async def test_get_task_analytics_progress_trends(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=10),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=10.0,
        done_hr=6.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=True,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    # Create progress history with improving trend
    progress_history = [
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=9),
            end_date=datetime.now(timezone.utc) - timedelta(days=8),
            status="completed",
            done_hr=2.0,
            estimated_hr=3.0
        ),
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=7),
            end_date=datetime.now(timezone.utc) - timedelta(days=6),
            status="completed",
            done_hr=2.5,
            estimated_hr=3.0
        ),
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=5),
            end_date=datetime.now(timezone.utc) - timedelta(days=4),
            status="completed",
            done_hr=3.0,
            estimated_hr=3.0
        ),
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=3),
            end_date=datetime.now(timezone.utc) - timedelta(days=2),
            status="completed",
            done_hr=3.5,
            estimated_hr=3.0
        )
    ]
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=progress_history)
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    progress_trends = result["analytics"]["progress_trends"]
    
    assert progress_trends["cycles_analyzed"] == 4
    assert progress_trends["recent_performance"] == [3.0, 3.5]  # Last 2 cycles
    assert progress_trends["trend"] == "improving"  # Should detect improvement

@pytest.mark.asyncio
async def test_get_task_analytics_performance_indicators(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=5),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=10.0,
        done_hr=6.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=True,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    progress_history = [
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=4),
            end_date=datetime.now(timezone.utc) - timedelta(days=3),
            status="completed",
            done_hr=3.0,
            estimated_hr=3.0
        ),
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=2),
            end_date=datetime.now(timezone.utc) - timedelta(days=1),
            status="completed",
            done_hr=3.0,
            estimated_hr=3.0
        )
    ]
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=progress_history)
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    performance_indicators = result["analytics"]["performance_indicators"]
    
    assert performance_indicators["productivity_score"] == 100.0  # 6/6 * 100
    assert performance_indicators["reliability_score"] == 100.0   # All cycles met estimates
    assert performance_indicators["quality_score"] == 100.0       # All cycles completed 100%
    assert performance_indicators["overall_performance"] == 100.0

@pytest.mark.asyncio
async def test_get_task_analytics_status_analysis(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=5),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=10.0,
        done_hr=6.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=True,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=[])
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    status_analysis = result["analytics"]["status_analysis"]
    
    assert status_analysis["current_status"] == "in_progress"
    assert status_analysis["status_health"] == "good"  # in_progress with done_hr > 0
    assert status_analysis["is_repetitive"] == True
    assert status_analysis["is_stopped"] == False
    assert status_analysis["status_duration_days"] >= 4  # Should be around 5 days

@pytest.mark.asyncio
async def test_get_task_analytics_time_analysis(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=5),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=10.0,
        done_hr=6.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=[])
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    time_analysis = result["analytics"]["time_analysis"]
    
    assert time_analysis["time_spent_hours"] >= 110  # ~5 days * 24 hours
    assert time_analysis["time_remaining_hours"] >= 110  # ~5 days * 24 hours
    assert time_analysis["deadline_status"] == "on_track"  # Still has time
    assert time_analysis["start_date"] == task.start_date
    assert time_analysis["end_date"] == task.end_date

@pytest.mark.asyncio
async def test_get_task_analytics_summary(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=5),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=10.0,
        done_hr=6.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=[])
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    summary = result["analytics"]["summary"]
    
    assert "grade" in summary
    assert "overall_score" in summary
    assert "recommendations" in summary
    assert "key_insights" in summary
    assert len(summary["recommendations"]) > 0
    assert len(summary["key_insights"]) > 0

@pytest.mark.asyncio
async def test_get_task_analytics_no_progress(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=5),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=10.0,
        done_hr=0.0,
        owner_id=current_user.id,
        status="pending",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=[])
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    analytics = result["analytics"]
    
    assert analytics["completion_metrics"]["completion_rate"] == 0.0
    assert analytics["time_efficiency"]["efficiency_score"] == 0.0
    assert analytics["progress_trends"]["trend"] == "no_data"
    assert analytics["performance_indicators"]["overall_performance"] == 0.0
    assert analytics["status_analysis"]["status_health"] == "needs_attention"

@pytest.mark.asyncio
async def test_get_task_analytics_permission_error(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Test Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=5),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=10.0,
        done_hr=6.0,
        owner_id=999,  # Different user
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    
    with pytest.raises(PermissionError, match="You don't have access to this task"):
        await service.get_task_analytics(1, current_user)

@pytest.mark.asyncio
async def test_get_task_analytics_task_not_found(service, mock_uow, current_user):
    mock_uow.tasks.get_task = AsyncMock(return_value=None)
    
    with pytest.raises(NotFoundError, match="Task not found"):
        await service.get_task_analytics(1, current_user)

# Additional test coverage for missing functionality

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
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    
    result = await service.get_task(1, current_user)
    
    assert result == task
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
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    
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
    
    result = await service.get_task(1, current_user)
    
    assert result == task

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
        subtasks=[],
        assignees=[]
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
        subtasks=[],
        assignees=[2]  # Assigned user
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.assign_user_to_task = AsyncMock()
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
    
    assert result == True
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

# Additional analytics edge cases

@pytest.mark.asyncio
async def test_analytics_completed_task(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Completed Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=10),
        end_date=datetime.now(timezone.utc) - timedelta(days=1),
        estimated_hr=10.0,
        done_hr=10.0,
        owner_id=current_user.id,
        status="completed",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=[])
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    analytics = result["analytics"]
    
    assert analytics["completion_metrics"]["completion_rate"] == 100.0
    assert analytics["status_analysis"]["status_health"] == "excellent"
    assert analytics["summary"]["grade"] == "A"

@pytest.mark.asyncio
async def test_analytics_overdue_task(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Overdue Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=10),
        end_date=datetime.now(timezone.utc) - timedelta(days=1),  # Past deadline
        estimated_hr=10.0,
        done_hr=5.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=[])
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    analytics = result["analytics"]
    
    assert analytics["time_analysis"]["deadline_status"] == "overdue"
    assert analytics["completion_metrics"]["completion_rate"] == 50.0
    assert "urgent" in analytics["summary"]["recommendations"][0].lower()

@pytest.mark.asyncio
async def test_analytics_repetitive_task_with_stops(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Repetitive Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=10),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=10.0,
        done_hr=6.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=True,
        is_stopped=True,
        subtasks=[],
        assignees=[]
    )
    
    stop_history = [{"id": 1, "stopped_at": datetime.now(timezone.utc) - timedelta(days=5)}]
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=[])
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=stop_history)
    
    result = await service.get_task_analytics(1, current_user)
    analytics = result["analytics"]
    
    assert analytics["status_analysis"]["stop_frequency"] == 1
    assert analytics["status_analysis"]["is_stopped"] == True
    assert "resuming" in analytics["summary"]["recommendations"][0].lower()

@pytest.mark.asyncio
async def test_analytics_task_with_no_dates(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Task with no dates",
        start_date=None,
        end_date=None,
        estimated_hr=10.0,
        done_hr=5.0,
        owner_id=current_user.id,
        status="pending",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=[])
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    analytics = result["analytics"]
    
    assert analytics["time_analysis"]["deadline_status"] == "no_deadline"
    assert analytics["time_analysis"]["time_spent_hours"] == 0
    assert analytics["time_analysis"]["time_remaining_hours"] == 0

@pytest.mark.asyncio
async def test_analytics_high_variance_progress(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="High Variance Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=10),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=10.0,
        done_hr=6.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=True,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    # Progress with high variance (inconsistent work patterns)
    progress_history = [
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=9),
            end_date=datetime.now(timezone.utc) - timedelta(days=8),
            status="completed",
            done_hr=1.0,  # Very low
            estimated_hr=3.0
        ),
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=7),
            end_date=datetime.now(timezone.utc) - timedelta(days=6),
            status="completed",
            done_hr=5.0,  # Very high
            estimated_hr=3.0
        ),
        TaskProgressDomain(
            task_id=1,
            start_date=datetime.now(timezone.utc) - timedelta(days=5),
            end_date=datetime.now(timezone.utc) - timedelta(days=4),
            status="completed",
            done_hr=0.5,  # Very low again
            estimated_hr=3.0
        )
    ]
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=progress_history)
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    analytics = result["analytics"]
    
    # Should detect high variance (low consistency)
    assert analytics["progress_trends"]["consistency_score"] < 50
    assert analytics["performance_indicators"]["reliability_score"] < 100

@pytest.mark.asyncio
async def test_analytics_zero_estimated_hours(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Zero Estimated Hours Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=5),
        end_date=datetime.now(timezone.utc) + timedelta(days=5),
        estimated_hr=0.0,  # Zero estimated hours
        done_hr=5.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=[])
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    analytics = result["analytics"]
    
    # Should handle division by zero gracefully
    assert analytics["completion_metrics"]["completion_rate"] == 0.0
    assert analytics["completion_metrics"]["remaining_hours"] == 0.0
    assert analytics["time_efficiency"]["efficiency_score"] == 0.0

@pytest.mark.asyncio
async def test_analytics_very_large_numbers(service, mock_uow, current_user):
    task = TaskOutput(
        id=1,
        description="Large Numbers Task",
        start_date=datetime.now(timezone.utc) - timedelta(days=100),
        end_date=datetime.now(timezone.utc) + timedelta(days=100),
        estimated_hr=1000.0,  # Very large estimate
        done_hr=500.0,
        owner_id=current_user.id,
        status="in_progress",
        is_repititive=False,
        is_stopped=False,
        subtasks=[],
        assignees=[]
    )
    
    mock_uow.tasks.get_task = AsyncMock(return_value=task)
    mock_uow.tasks.get_progress = AsyncMock(return_value=[])
    mock_uow.tasks.get_stop_progress = AsyncMock(return_value=[])
    
    result = await service.get_task_analytics(1, current_user)
    analytics = result["analytics"]
    
    # Should handle large numbers correctly
    assert analytics["completion_metrics"]["completion_rate"] == 50.0
    assert analytics["completion_metrics"]["remaining_hours"] == 500.0
    assert analytics["time_analysis"]["time_spent_hours"] >= 2400  # ~100 days * 24 hours
