from datetime import datetime, timezone
from domain.exceptions import BadRequestError, NotFoundError
from domain.models.task_model import TaskCreateInput, TaskOutput, TaskProgressDomain
from domain.repositories.iuow import IUnitOfWork

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
                if main_task.owner_id != current_user.id and current_user.id not in main_task.assignees:
                    raise PermissionError("Cannot create subtask for another user's task")

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

        if task.owner_id == current_user.id or current_user.id in [u.id for u in task.assignees]:
            return task

        raise PermissionError("You don't have access to this task")

    async def get_tasks(self, current_user, skip: int = 0, limit: int = 100):
        result = []
        async with self.uow:
            try:
                tasks = await self.uow.tasks.get_tasks(skip=skip, limit=limit)

                for task in tasks:
                    if task.owner_id == current_user.id or current_user.id in [u.id for u in task.assignees]:
                        await self._handle_repetitive_task(task)
                        result.append(task)
            except Exception:
                await self.uow.rollback()
                raise
            else:
                await self.uow.commit()
            return result


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
            if current_user.id != task.owner_id and current_user.id not in [u.id for u in task.assignees]:
                raise PermissionError("You don't have permission to update this task")

            if "start_date" in task_data:
                task_data["start_date"] = self._normalize_datetime(task_data["start_date"])
            if "end_date" in task_data:
                task_data["end_date"] = self._normalize_datetime(task_data["end_date"])

            if task_data.get("end_date") and task_data.get("start_date"):
                if task_data["end_date"] < task_data["start_date"]:
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
                if current_user.id != task.owner_id and current_user.id not in [u.id for u in task.assignees]:
                    raise PermissionError("You don't have permission to update this task")
                if not task.is_repititive:
                    raise BadRequestError("This task is not repetitive")

                if not task.is_stopped and stop:
                    await self.uow.tasks.update_task(task_id, {"is_stopped": True})
                    await self.uow.tasks.create_stop(task_id)
                    result = {"message": "task stopped successfully"}

                elif task.is_stopped and not stop:
                    stopped = await self.uow.tasks.get_stop(task_id)
                    await self.uow.tasks.update_task(
                        task_id,
                        {
                            "is_stopped": False,
                            "start_date": datetime.now(timezone.utc)
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
        if current_user.id != task.owner_id and current_user.id not in [u.id for u in task.assignees]:
            raise PermissionError("You don't have permission to view this task's progress")

        return await self.uow.tasks.get_progress(task_id, skip, limit)