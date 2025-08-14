from typing import List, Optional

from api.dependencies import get_current_user, get_task_service
from api.dto import task_dto
from api.schemas.task_schema import (
    AssignUserInput,
    Task,
    TaskCreate,
    TaskProgress,
    TaskUpdate,
)
from api.utilities.handle_service_result import handle_service_result
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/", response_model=Task)
@handle_service_result
async def create_task(
    task: TaskCreate,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    task = task_dto.pydantic_to_domain_task_create(task)
    result = await service.create_task(task, current_user)  # await async service
    return result


@router.get("/", response_model=List[Task])
@handle_service_result
async def read_tasks(
    skip: int = 0,
    limit: int = 10,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    result = await service.get_tasks(current_user=current_user, skip=skip, limit=limit)
    return result


@router.get("/{task_id}", response_model=Task)
@handle_service_result
async def read_task(
    task_id: int,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    result = await service.get_task(task_id, current_user)
    return result


@router.delete("/{task_id}")
@handle_service_result
async def delete_task(
    task_id: int,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    result = await service.delete_task(task_id, current_user)
    return result


@router.post("/assign/{task_id}", response_model=Task)
@handle_service_result
async def assign_user_to_task(
    task_id: int,
    data: AssignUserInput,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    result = await service.assign_user_to_task(task_id, data.assignee_email, current_user)
    return result


@router.patch("/{task_id}", response_model=Task)
@handle_service_result
async def update_task(
    task_id: int,
    data: TaskUpdate,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    task_data = data.model_dump(exclude_unset=True)
    result = await service.update_task(task_id, task_data, current_user)
    return result


@router.post("/start/{task_id}")
@handle_service_result
async def start_task(
    task_id: int,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    result = await service.toggle_task(task_id, False, current_user)
    return result


@router.post("/stop/{task_id}")
@handle_service_result
async def stop_task(
    task_id: int,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    result = await service.toggle_task(task_id, True, current_user)
    return result


@router.get("/progress/{task_id}", response_model=List[TaskProgress])
@handle_service_result
async def task_progress(
    task_id: int,
    skip: Optional[int] = 0,
    limit: Optional[int] = 20,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    return await service.get_progress(task_id, current_user, skip, limit)
