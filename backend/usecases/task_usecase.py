from datetime import datetime, timezone

from domain.exceptions import BadRequestError, NotFoundError
from domain.Models import TaskCreateInput, TaskOutput


class TaskService:
    def __init__(self, repo):
        self.repo = repo

    def _to_task_output(self, task_orm) -> TaskOutput:
        return TaskOutput(
            id=task_orm.id,
            description=task_orm.description,
            end_date=task_orm.end_date,
            estimated_hr=task_orm.estimated_hr,
            is_repititive=task_orm.is_repititive,
            status=task_orm.status,
            start_date=task_orm.start_date,
            main_task_id=task_orm.main_task_id,
            subtasks=[sub.id for sub in getattr(task_orm, "subtasks", [])],
            assignees=[u.id for u in getattr(task_orm, "assignees", [])],
            owner_id=task_orm.owner_id,
        )

    def _handle_repetitive_task(self, task, max_cycle=100):
        now = datetime.now(timezone.utc)
        updated = False
        cycle = 0
        while task.is_repititive and task.end_date <= now and not task.is_stopped:
            # Save current progress
            if cycle >= max_cycle:
                return
            cycle += 1
            self.repo.create_progress(
                {
                    "task_id": task.id,
                    "start_date": task.start_date,
                    "end_date": task.end_date,
                    "status": task.status,
                    "done_hr": task.done_hr,
                    "estimated_hr": task.estimated_hr,
                }
            )

            # Update the task for the next period
            interval = task.end_date - task.start_date
            task.start_date = task.end_date
            task.end_date += interval
            task.status = "in_progress"
            task.done_hr = 0.0
            updated = True

        if updated:
            self.repo.update_task(task)

    def create_task(self, task: TaskCreateInput, current_user):
        task_data = task.__dict__
        task_data["owner_id"] = current_user.id
        if task_data.get("main_task_id"):
            main_task = self.repo.get_task(task_data["main_task_id"])
            if not main_task:
                raise NotFoundError("Main task not found")
            if main_task.owner_id != current_user.id:
                raise PermissionError("Cannot create subtask for another user's task")

        # Validate start date
        if not task_data.get("start_date"):
            task_data["start_date"] = datetime.now(timezone.utc)
        elif task_data["start_date"] < datetime.now(timezone.utc):
            raise BadRequestError("Start date cannot be in the past")
        if task_data["estimated_hr"] < 0:
            raise BadRequestError("Estimated hours cannot be negative")
        # Validate end date
        if task_data["end_date"] < task_data["start_date"]:
            raise BadRequestError("End date cannot be before start date")

        task = self.repo.create_task(task_data)
        return self._to_task_output(task)

    def get_task(self, task_id: int, current_user):
        task = self.repo.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")

        if task.owner_id == current_user.id or current_user.id in [
            u.id for u in task.assignees
        ]:
            return self._to_task_output(task)

        raise PermissionError("You don't have access to this task")

    def get_tasks(self, current_user, skip: int = 0, limit: int = 100):
        tasks = self.repo.get_tasks(skip=skip, limit=limit)
        result = []

        for task in tasks:
            if task.owner_id == current_user.id or current_user.id in [
                u.id for u in task.assignees
            ]:
                self._handle_repetitive_task(task)
                result.append(self._to_task_output(task))

        return result

    def delete_task(self, task_id: int, current_user):
        if not self.repo.delete_task(task_id, current_user.id):
            raise ValueError("Delete failed. Task not found or not allowed.")
        return True

    def assign_user_to_task(self, task_id: int, assignee_email: str, current_user):
        task = self.repo.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")
        if task.owner_id != current_user.id:
            raise BadRequestError("You are not authorized to assign this task")

        task, error = self.repo.assign_user_to_task(task_id, assignee_email)
        if error:
            raise BadRequestError(error)

        return self._to_task_output(task)

    def update_task(self, task_id: int, task_data: dict, current_user):
        task = self.repo.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")
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
        if task_data.get("estimated_hr"):
            if task_data["estimated_hr"] < 0:
                raise BadRequestError("Estimated hours cannot be negative")
        updated_task = self.repo.update_task(task_id, task_data)
        return self._to_task_output(updated_task)
