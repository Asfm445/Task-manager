from domain.models.task_model import (
    TaskCreateInput,
    TaskOutput,
    TaskProgressDomain,
    TaskStatus,
)
from infrastructure.models.model import Task as ORMTask
from infrastructure.models.model import TaskProgress as ORMTaskProgress


def domain_to_orm_task_create(domain_task: TaskCreateInput, owner_id: int) -> ORMTask:
    orm_task = ORMTask(
        description=domain_task.description,
        end_date=domain_task.end_date,
        estimated_hr=domain_task.estimated_hr,
        is_repititive=domain_task.is_repititive,
        status=domain_task.status.value,  # Enum to string
        start_date=domain_task.start_date,
        main_task_id=domain_task.main_task_id,
        owner_id=owner_id,
        done_hr=0.0,
        is_stopped=False,
    )
    return orm_task


def orm_to_domain_task_output(orm_task: ORMTask) -> TaskOutput:
    return TaskOutput(
        id=orm_task.id,
        description=orm_task.description,
        end_date=orm_task.end_date,
        estimated_hr=orm_task.estimated_hr,
        is_repititive=orm_task.is_repititive,
        status=orm_task.status,
        start_date=orm_task.start_date,
        main_task_id=orm_task.main_task_id,
        subtasks=(
            [subtask.id for subtask in orm_task.subtasks] if orm_task.subtasks else []
        ),
        assignees=(
            [user.id for user in orm_task.assignees] if orm_task.assignees else []
        ),
        owner_id=orm_task.owner_id,
    )


# Pydantic -> Domain


# Domain -> ORM


def domain_to_orm_task_progress(domain: TaskProgressDomain) -> ORMTaskProgress:
    orm = ORMTaskProgress(
        task_id=domain.task_id,
        start_date=domain.start_date,
        end_date=domain.end_date,
        status=(
            domain.status.value
            if isinstance(domain.status, TaskStatus)
            else domain.status
        ),
        done_hr=domain.done_hr,
        estimated_hr=domain.estimated_hr,
    )
    return orm


# ORM -> Domain


def orm_to_domain_task_progress(orm: ORMTaskProgress) -> TaskProgressDomain:
    return TaskProgressDomain(
        task_id=orm.task_id,
        start_date=orm.start_date,
        end_date=orm.end_date,
        status=TaskStatus(orm.status),
        done_hr=orm.done_hr,
        estimated_hr=orm.estimated_hr,
    )
