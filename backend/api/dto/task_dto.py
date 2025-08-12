from api.schemas.task_schema import Task as PydanticTask
from api.schemas.task_schema import TaskCreate
from api.schemas.task_schema import TaskProgress as PydanticTaskProgress
from api.schemas.task_schema import TaskUpdate as PydanticTaskUpdate
from domain.models.task_model import (
    TaskCreateInput,
    TaskOutput,
    TaskProgressDomain,
    TaskUpdateInput,
)


def domain_to_pydantic_task(domain_task: TaskOutput) -> PydanticTask:
    return PydanticTask(
        id=domain_task.id,
        description=domain_task.description,
        end_date=domain_task.end_date,
        estimated_hr=domain_task.estimated_hr,
        is_repititive=domain_task.is_repititive,
        status=domain_task.status,
        start_date=domain_task.start_date,
        main_task_id=domain_task.main_task_id,
        subtasks=domain_task.subtasks,
        assignees=domain_task.assignees,
        owner_id=domain_task.owner_id,
        done_hr=0.0,  # If you want to add done_hr from domain, add it to TaskOutput model
        is_stopped=False,  # Similarly for is_stopped
    )


def pydantic_to_domain_task_create(pydantic_task: TaskCreate) -> TaskCreateInput:
    return TaskCreateInput(
        description=pydantic_task.description,
        end_date=pydantic_task.end_date,
        estimated_hr=pydantic_task.estimated_hr,
        is_repititive=pydantic_task.is_repititive,
        status=pydantic_task.status,
        start_date=pydantic_task.start_date,
        main_task_id=pydantic_task.main_task_id,
    )


def pydantic_to_domain_task_update(p: PydanticTaskUpdate) -> TaskUpdateInput:
    return TaskUpdateInput(
        description=p.description,
        end_date=p.end_date,
        estimated_hr=p.estimated_hr,
        is_repititive=p.is_repititive,
        status=p.status,
        start_date=p.start_date,
        main_task_id=p.main_task_id,
    )


def pydantic_to_domain_task_progress(p: PydanticTaskProgress) -> TaskProgressDomain:
    return TaskProgressDomain(
        task_id=p.task_id,
        start_date=p.start_date,
        end_date=p.end_date,
        status=p.status,
        done_hr=p.done_hr,
        estimated_hr=p.estimated_hr,
    )
