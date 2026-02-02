from datetime import datetime, timezone
from typing import Any, Dict, List

from domain.exceptions import BadRequestError, NotFoundError
from domain.interfaces.iuow import IUnitOfWork
from domain.models.task_model import TaskCreateInput, TaskOutput, TaskProgressDomain, SubTaskOutput, TaskProgressAnalytics, TaskStatus


class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def _normalize_datetime(self, dt):
        if dt and dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _validate_dates(self, start_date, end_date):
        start_date = self._normalize_datetime(start_date)
        end_date = self._normalize_datetime(end_date)
        if start_date and end_date < start_date:
            raise BadRequestError("End date cannot be before start date")
    
    async def _handle_repetitive_task(self, task: TaskOutput, max_cycle=100):
        
        now = datetime.now(timezone.utc)
        updated = False
        cycle = 0
        
        while task.is_repititive and task.end_date <= now and not task.is_stopped:

            if cycle >= max_cycle:
                return
            cycle += 1
            await self.uow.tasks.create_progress(
                TaskProgressDomain(
                    **{
                        "task_id": task.id,
                        "start_date": task.start_date,
                        "end_date": task.end_date,
                        "status": task.status,
                        "done_hr": task.done_hr,
                        "estimated_hr": task.estimated_hr,
                    }
                )
            )
            interval = task.end_date - task.start_date
            data={
                "start_date": task.end_date,
                "end_date": task.end_date + interval,
                "status": "in_progress",
                "done_hr": 0.0,

            }
            task.start_date = task.end_date
            task.end_date += interval
            task.status = "in_progress"
            task.done_hr = 0.0
            updated = True

        if updated:
            await self.uow.tasks.update_task(task.id, data)


    async def create_task(self, task: TaskCreateInput, current_user):
        async with self.uow:
            if task.main_task_id:
                main_task = await self.uow.tasks.get_task(task.main_task_id)
                if not main_task:
                    raise NotFoundError("Main task not found")
                main_task_assignees= await self.uow.tasks.get_assignees_of_task(task.main_task_id)
                if main_task.owner_id != current_user.id and current_user.id not in main_task_assignees:
                    raise PermissionError("You are not authorized to create subtask for another user's task")

            if not task.start_date:
                task.start_date = datetime.now(timezone.utc)

            task.start_date = self._normalize_datetime(task.start_date)
            task.end_date = self._normalize_datetime(task.end_date)

            if task.estimated_hr < 0:
                raise BadRequestError("Estimated hours cannot be negative")

            self._validate_dates(task.start_date, task.end_date)
            created_task = await self.uow.tasks.create_task(task, current_user.id)
            return created_task

    async def get_task(self, task_id: int, current_user):
        task = await self.uow.tasks.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")
        
        task_assginess=await self.uow.tasks.get_assignees_of_task_email(task.id)
        sub_tasks=await self.uow.tasks.get_desription_and_id_of_subtasks(task.id)
        task.subtasks = [SubTaskOutput(id=id, description=description) for description, id in sub_tasks]
        task.assignees = task_assginess
        if task.is_repititive:
            progresses=await self.uow.tasks.get_progress(task.id)
            progresses=progresses["data"]
            if progresses and len(progresses)>0:
                total_estimated_hr=0
                total_done_hr=0
                total_stopped_hr=0
                completed=0
                for progress in progresses:
                    if progress.status != "stopped":
                        total_estimated_hr += progress.estimated_hr
                        total_done_hr += progress.done_hr
                        if progress.status == "completed":
                            completed += 1
                    else:
                        stopped_time = progress.end_date - progress.start_date
                        total_stopped_hr += stopped_time.total_seconds() / 3600

                if total_estimated_hr > 0:
                    accuracy = total_done_hr / total_estimated_hr
                else:
                    accuracy = 0
                if len(progresses) > 0:
                    completion_rate = completed / len(progresses)
                else:
                    completion_rate = 0
                progress = TaskProgressAnalytics(
                    done_hr=total_done_hr,
                    estimated_hr=total_estimated_hr,
                    accuracy=accuracy,
                    completion_rate=completion_rate,
                    stopped_hr=total_stopped_hr,
                )
        else:
            progress = None
        
        now = datetime.now(timezone.utc)
        if task.estimated_hr > 0:
            curr_completion_rate = task.done_hr / task.estimated_hr
        else:
            curr_completion_rate = 0

        total_duration = (task.end_date - task.start_date).total_seconds()
        if total_duration > 0:
            elapsed_duration = (now - task.start_date).total_seconds()
            standard_completion_hr = (elapsed_duration / total_duration) * task.estimated_hr
        else:
            standard_completion_hr = 0
    
            
        if task.owner_id == current_user.id or current_user.email in task_assginess:
            async with self.uow:
                try:
                    await self._handle_repetitive_task(task)
                except Exception:
                    await self.uow.rollback()
                    raise
                else:
                    await self.uow.commit()
            return {"task": task, "progress": progress, "standard_completion_hr": standard_completion_hr, "curr_completion_rate": curr_completion_rate}

        raise PermissionError("You don't have access to this task")


    async def get_tasks(self, current_user,search_name=None, skip: int = 0, limit: int = 100, uncompleted=False, completed=False):
        print("+++++++++++++++++++++++++++++++++++++hre in usecase before fetching++++++++++++++++++++++")
        tasks = await self.uow.tasks.get_tasks(
            current_user.id,
            skip=skip,
            limit=limit,
            search_name=search_name,
            uncompleted=uncompleted,
            completed=completed,
        )
        print("+++++++++++++++++++++++++++++++++++++hre in usecase after fetching++++++++++++++++++++++")
        num = len(tasks)
        tasks.sort(key=lambda x: x.end_date)
        return {"tasks": tasks, "total": num}


    async def delete_task(self, task_id: int, current_user):
        async with self.uow:
            task = await self.uow.tasks.get_task(task_id)
            if not task:
                raise NotFoundError("Task not found")
            if task.owner_id != current_user.id:
                raise PermissionError("Cannot delete another user's task")
            
            await self.uow.tasks.delete_task(task_id,current_user.id)
            return True

    async def assign_user_to_task(self, task_id: int, assignee_email: str, current_user):
        async with self.uow:
            task = await self.uow.tasks.get_task(task_id)
            if not task:
                raise NotFoundError("Task not found")
            if current_user.id != task.owner_id:
                raise PermissionError("You are not authorized to assign this task")

            await self.uow.tasks.assign_user_to_task(task_id, assignee_email)
            return await self.uow.tasks.get_task(task_id)

    async def update_task(self, task_id: int, task_data: dict, current_user):
        async with self.uow:
            task = await self.uow.tasks.get_task(task_id)
            if not task:
                raise NotFoundError("Task not found")
            if current_user.id != task.owner_id and current_user.id not in task.assignees:
                raise PermissionError("You don't have permission to update this task")

            if "start_date" in task_data:
                task_data["start_date"] = self._normalize_datetime(task_data["start_date"])
            if "end_date" in task_data:
                task_data["end_date"] = self._normalize_datetime(task_data["end_date"])

            # Validate dates (handling partial updates)
            start_date_to_check = task_data.get("start_date") or task.start_date
            end_date_to_check = task_data.get("end_date") or task.end_date

            # Ensure they are normalized if they came from existing task (already normalized usually, but good for safety)
            # If they came from task_data they are already normalized above
            
            if start_date_to_check and end_date_to_check:
                 if end_date_to_check < start_date_to_check:
                    raise BadRequestError("End date cannot be before start date")

            if task_data.get("estimated_hr") is not None and task_data["estimated_hr"] < 0:
                raise BadRequestError("Estimated hours cannot be negative")

            return await self.uow.tasks.update_task(task_id, task_data)

    async def toggle_task(self, task_id: int, stop: bool, current_user):
        result = None
        async with self.uow:
            try:
                task = await self.uow.tasks.get_task(task_id)
                if not task:
                    raise NotFoundError("Task not found")
                if current_user.id != task.owner_id and current_user.id not in task.assignees:
                    raise PermissionError("You don't have permission to update this task")
                if not task.is_repititive:
                    raise BadRequestError("This task is not repetitive")

                if not task.is_stopped and stop:
                    await self.uow.tasks.update_task(task_id, {"is_stopped": True})
                    await self.uow.tasks.create_stop(task_id)
                    result = {"message": "task stopped successfully"}

                elif task.is_stopped and not stop:
                    stopped = await self.uow.tasks.get_stop(task_id)
                    interval=task.end_date-task.start_date
                    await self.uow.tasks.update_task(
                        task_id,
                        {
                            "is_stopped": False,
                            "start_date": datetime.now(timezone.utc),
                            "end_date": datetime.now(timezone.utc)+interval,
                        }
                    )
                    await self.uow.tasks.create_progress(
                        TaskProgressDomain(
                            task_id=task.id,
                            start_date=stopped.stopped_at,
                            end_date=datetime.now(timezone.utc),
                            status="stopped",
                            done_hr=0,
                            estimated_hr=0
                        )
                    )
                    await self.uow.tasks.delete_stop(task_id)
                    result = {"message": "task started successfully"}

                elif task.is_stopped:
                    raise BadRequestError("task is already stopped")
                else:
                    raise BadRequestError("task is already running")

            except Exception:
                await self.uow.rollback()
                raise
            else:
                await self.uow.commit()

        return result

            

    async def get_progress(self, task_id: int, current_user, skip=0, limit=20):
        task = await self.uow.tasks.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")
        if current_user.id != task.owner_id and current_user.id not in task.assignees:
            raise PermissionError("You don't have permission to view this task's progress")

        result=await self.uow.tasks.get_progress(task_id, skip, limit)
        return result