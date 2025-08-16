import pytest
from datetime import datetime, timezone, timedelta

from infrastructure.repositories.task_repository import TaskRepository
from domain.models.task_model import TaskCreateInput
from domain.models.task_model import TaskProgressDomain

@pytest.mark.asyncio
async def test_create_and_get_task(async_session):
    repo = TaskRepository(async_session)
    
    # Create a task
    task_input = TaskCreateInput(
        description="Desc",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5,
        is_repititive=False
    )
    created_task = await repo.create_task(task_input, owner_id=1)
    
    # Fetch the task by ID
    fetched_task = await repo.get_task(created_task.id)
    
    assert fetched_task is not None
    assert fetched_task.owner_id == 1

    deleted_task= await repo.delete_task(fetched_task.id, fetched_task.owner_id)

    assert fetched_task is not None
    assert fetched_task.owner_id == 1

    fetched_task = await repo.get_task(created_task.id)

    assert fetched_task is None

@pytest.mark.asyncio
async def test_update_task(async_session):
    repo = TaskRepository(async_session)
    
    # Create task
    task_input = TaskCreateInput(
        description="Desc",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=3,
        is_repititive=False
    )
    task = await repo.create_task(task_input, owner_id=1)
    
    # Update task
    updated_task = await repo.update_task(task.id, {"description": "upd"})
    
    assert updated_task.description == "upd"

@pytest.mark.asyncio
async def test_assign_user_to_task(async_session):
    from infrastructure.models.model import User
    repo = TaskRepository(async_session)
    
    # Add a user
    user = User(email="user@test.com", username="testuser")
    async_session.add(user)
    await async_session.flush()
    
    # Create task
    task_input = TaskCreateInput(
        description="Desc",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=2,
        is_repititive=False
    )
    task = await repo.create_task(task_input, owner_id=1)
    
    # Assign user
    assigned_task, error = await repo.assign_user_to_task(task.id, "user@test.com")
    
    assert error is None
    assert assigned_task is not None
    assert len(assigned_task.assignees) == 1


@pytest.mark.asyncio
async def test_progress_and_stop(async_session):
    repo = TaskRepository(async_session)
    
    # Create a task
    task_input = TaskCreateInput(
        description="Desc",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hr=5,
        is_repititive=False
    )
    task = await repo.create_task(task_input, owner_id=1)

    progress=TaskProgressDomain(
                    **{
                        "task_id": task.id,
                        "start_date": task.start_date,
                        "end_date": task.end_date,
                        "status": task.status,
                        "done_hr": task.done_hr,
                        "estimated_hr": task.estimated_hr,
                    }
                )
    created_prg= await repo.create_progress(progress)

    assert created_prg is not None
    assert created_prg.task_id==task.id

    stop=await repo.create_stop(task.id)

    assert stop is not None
    assert stop.task_id== task.id

    fetched_stop=await repo.get_stop(task.id)

    assert fetched_stop is not None
    assert fetched_stop.task_id== task.id
    assert fetched_stop.stopped_at==stop.stopped_at

    await repo.delete_stop(task.id)


    stop=await repo.get_stop(task.id)

    assert stop is None





