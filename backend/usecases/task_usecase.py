from datetime import datetime, timezone

from domain.exceptions import BadRequestError, NotFoundError
from domain.models.task_model import TaskCreateInput, TaskOutput, TaskProgressDomain
from domain.repositories.task_repo import AbstractTaskRepository


class TaskService:
    def __init__(self, repo: AbstractTaskRepository):
        self.repo = repo

    def _normalize_datetime(self, dt):
        if dt and dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _validate_dates(self, start_date, end_date):
        start_date = self._normalize_datetime(start_date)
        end_date = self._normalize_datetime(end_date)
        now = datetime.now(timezone.utc)

        if start_date and start_date < now:
            raise BadRequestError("Start date cannot be in the past")
        if end_date:
            if end_date < now:
                raise BadRequestError("End date cannot be in the past")
            if start_date and end_date < start_date:
                raise BadRequestError("End date cannot be before start date")

    async def _handle_repetitive_task(self, task: TaskOutput, max_cycle=100):
        now = datetime.now()
        updated = False
        cycle = 0
        while task.is_repititive and task.end_date <= now and not task.is_stopped:
            if cycle >= max_cycle:
                return
            cycle += 1
            await self.repo.create_progress(
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
            await self.repo.update_task(task.id, data)



    async def create_task(self, task: TaskCreateInput, current_user):
        if task.main_task_id:
            main_task = await self.repo.get_task(task.main_task_id)
            if not main_task:
                raise NotFoundError("Main task not found")
            if main_task.owner_id != current_user.id:
                raise PermissionError("Cannot create subtask for another user's task")

        if not task.start_date:
            task.start_date = datetime.now(timezone.utc)

        task.start_date = self._normalize_datetime(task.start_date)
        task.end_date = self._normalize_datetime(task.end_date)

        if task.estimated_hr < 0:
            raise BadRequestError("Estimated hours cannot be negative")

        self._validate_dates(task.start_date, task.end_date)

        task = await self.repo.create_task(task, current_user.id)
        return task

    async def get_task(self, task_id: int, current_user):
        task = await self.repo.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")

        if task.owner_id == current_user.id or current_user.id in task.assignees:
            return task

        raise PermissionError("You don't have access to this task")

    async def get_tasks(self, current_user, skip: int = 0, limit: int = 100):
        tasks = await self.repo.get_tasks(skip=skip, limit=limit)
        result = []

        for task in tasks:
            if task.owner_id == current_user.id or current_user.id in task.assignees:
                await self._handle_repetitive_task(task)
                result.append(task)

        return result

    async def delete_task(self, task_id: int, current_user):
        if not await self.repo.delete_task(task_id, current_user.id):
            raise ValueError("Delete failed. Task not found or not allowed.")
        return True

    async def assign_user_to_task(self, task_id: int, assignee_email: str, current_user):
        task = await self.repo.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")
        if current_user.id != task.owner_id:
            raise PermissionError("You are not authorized to assign this task")

        task, error = await self.repo.assign_user_to_task(task_id, assignee_email)
        if error:
            raise BadRequestError(error)

        return task

    async def update_task(self, task_id: int, task_data: dict, current_user):
        task = await self.repo.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")
        if current_user.id != task.owner_id and current_user.id not in [
            u.id for u in task.assignees
        ]:
            raise PermissionError("You don't have permission to update this task")

        if "start_date" in task_data:
            task_data["start_date"] = self._normalize_datetime(task_data["start_date"])
        if "end_date" in task_data:
            task_data["end_date"] = self._normalize_datetime(task_data["end_date"])
        task.start_date = self._normalize_datetime(task.start_date)

        if task_data.get("end_date") and task_data.get("start_date"):
            if task_data["end_date"] < task_data["start_date"]:
                raise BadRequestError("End date cannot be before start date")

        if task_data.get("start_date"):
            if task_data["start_date"] < datetime.now(timezone.utc):
                raise BadRequestError("Start date cannot be in the past")
        elif task_data.get("end_date"):
            if task_data["end_date"] < datetime.now(timezone.utc):
                raise BadRequestError("End date cannot be in the past")
            if task_data["end_date"] < task.start_date:
                raise BadRequestError("End date cannot be before start date")

        if task_data.get("estimated_hr") is not None and task_data["estimated_hr"] < 0:
            raise BadRequestError("Estimated hours cannot be negative")

        updated_task = await self.repo.update_task(task_id, task_data)
        return updated_task

    async def toggle_task(self, task_id: int, stop: bool, current_user):
        task = await self.repo.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")
        if current_user.id != task.owner_id and current_user.id not in [
            u.id for u in task.assignees
        ]:
            raise PermissionError("You don't have permission to update this task")
        if not task.is_repititive:
            raise BadRequestError("This task is not repetitive")
        if not task.is_stopped and stop:
            task.is_stopped = stop
            await self.repo.create_stop(task_id)
            await self.repo.update_task(task_id, {"is_stopped": stop})
            return {"message": "task stopped successfully"}
        elif task.is_stopped and not stop:
            task.is_stopped = stop
            await self.repo.update_task(
                task_id, {"is_stopped": stop, "start_date": datetime.now(timezone.utc)}
            )
            stopped = await self.repo.get_stop(task_id)
            print("+++++++++++++++++++++++++++++++printing+++++++++++++++++++")
            await self.repo.create_progress(
                TaskProgressDomain(**{
                    "task_id": task.id,
                    "start_date": stopped.stopped_at,
                    "end_date": datetime.now(timezone.utc),
                    "status": "stopped",
                    "done_hr": 0,
                    "estimated_hr": 0,
                })
            )
            await self.repo.delete_stop(task_id)
            return {"message": "task started successfully"}
        elif task.is_stopped:
            raise BadRequestError("task is already stopped")
        else:
            raise BadRequestError("task is already running")

    async def get_progress(self, task_id: int, current_user, skip=0, limit=20):
        task = await self.repo.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")
        if current_user.id != task.owner_id and current_user.id not in [
            u.id for u in task.assignees
        ]:
            raise PermissionError("You don't have permission to update this task")
        progress = await self.repo.get_progress(task_id, skip, limit)
        return progress
