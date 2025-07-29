from typing import List

from api.schemas.schema import AssignUserInput, Task, TaskCreate
from api.utilities.handle_service_result import handle_service_result
from auth.auth_get_user import get_current_user
from dependencies import get_task_service
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/", response_model=Task)
@handle_service_result
def create_task(
    task: TaskCreate,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    result = service.create_task(task, current_user)
    return result


@router.get("/", response_model=List[Task])
@handle_service_result
def read_tasks(
    skip: int = 0,
    limit: int = 10,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    result = service.get_tasks(current_user=current_user, skip=skip, limit=limit)
    return result


@router.get("/{task_id}", response_model=Task)
@handle_service_result
def read_task(
    task_id: int,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    result = service.get_task(task_id, current_user)
    return result


@router.delete("/{task_id}")
@handle_service_result
def delete_task(
    task_id: int,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    result = service.delete_task(task_id, current_user)
    return result


@router.put("/assign/{task_id}", response_model=Task)
@handle_service_result
def assign_user_to_task(
    task_id: int,
    data: AssignUserInput,
    service=Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    result = service.assign_user_to_task(task_id, data.assignee_email, current_user)
    return result
