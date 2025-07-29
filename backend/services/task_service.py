from datetime import datetime, timezone

from api.schemas import schema
from domain.exceptions import BadRequestError, NotFoundError


class TaskService:
    def __init__(self, repo):
        self.repo = repo

    def handleTask(self, task):
        task_dict = task.__dict__
        task_dict["subtasks"] = [subtask.id for subtask in task.subtasks]
        task_dict["assignees"] = [user.id for user in task.assignees]
        return schema.Task(**task_dict)

    def create_task(self, task: schema.TaskCreate, current_user):
        task_data = task.dict()

        # Subtask validation
        if task_data.get("main_task_id"):
            main_task = self.repo.get_task(task_data["main_task_id"])
            if not main_task:
                raise ValueError("Main task not found")
            if main_task.owner_id != current_user.id:
                raise PermissionError("Cannot create subtask for another user's task")

        # Start date validation
        if task_data.get("start_date"):
            if task_data["start_date"] < datetime.now(timezone.utc):
                raise ValueError("Start date cannot be in the past")
        else:
            task_data["start_date"] = datetime.now(timezone.utc)

        # End date validation
        if task_data["end_date"] < task_data["start_date"]:
            raise ValueError("End date cannot be before start date")

        task_data["owner_id"] = current_user.id

        created_task = self.repo.create_task(task_data)
        return self.handleTask(created_task)

    def get_task(self, task_id: int, current_user):
        task = self.repo.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")

        if task.owner_id == current_user.id or current_user.id in [
            u.id for u in task.assignees
        ]:
            return task

        raise PermissionError("You don't have access to this task")

    def get_tasks(self, current_user, skip: int = 0, limit: int = 100):
        tasks = self.repo.get_tasks(skip=skip, limit=limit)

        allowed_tasks = [
            task
            for task in tasks
            if task.owner_id == current_user.id or current_user in task.assignees
        ]

        # Handle repetitive tasks
        for task in allowed_tasks:
            while task.is_repititive and task.end_date <= datetime.now(timezone.utc):
                progress_data = {
                    "task_id": task.id,
                    "start_date": task.start_date,
                    "end_date": task.end_date,
                    "status": task.status,
                    "done_hr": task.done_hr,
                    "estimated_hr": task.estimated_hr,
                }
                self.repo.create_progress(progress_data)

                # Reset and extend task
                task.done_hr = 0.0
                task.status = "in_progress"
                interval = task.end_date - task.start_date
                task.start_date = task.end_date
                task.end_date += interval

                self.repo.update_task(task)

        return [self.handleTask(task) for task in allowed_tasks]

    def delete_task(self, task_id: int, current_user):
        deleted = self.repo.delete_task(task_id, current_user.id)
        if not deleted:
            raise ValueError("Delete failed. Task not found or not allowed.")
        return True
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
        return self.handleTask(task)
