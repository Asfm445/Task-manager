from datetime import date, datetime

from domain.exceptions import BadRequestError, NotFoundError
from domain.models.dayplan_model import TimeLogCreate
from domain.repositories.dayplan_repo import AbstractDayPlanRepository
from domain.repositories.task_repo import AbstractTaskRepository


class DayPlanUseCase:
    def __init__(
        self, repo: AbstractDayPlanRepository, task_repo: AbstractTaskRepository
    ):
        self.repo = repo
        self.task_repo = task_repo

    def _Duration(self, start_time: datetime, end_time: datetime) -> float:
        """Return duration between start_time \
        and end_time in hours (2 decimals)."""
        delta = end_time - start_time
        return round(delta.total_seconds() / 3600, 2)

    def delete_dayplan(self, date: date, current_user):
        dayplan = self.repo.get_dayplan(date, current_user)
        if not dayplan:
            raise NotFoundError("Dayplan not found")
        deleted_dayplan = self.repo.delete_dayplan(date, current_user)
        return deleted_dayplan  # Return domain model for router response

    def get_dayplan(self, date: date, current_user):
        dayplan = self.repo.get_dayplan(date, current_user)
        if not dayplan:
            dayplan = self.repo.create_dayplan(date, current_user)
        return dayplan  # domain model returned

    def create_time_log(self, time_log: TimeLogCreate, current_user):
        def to_naive(dt: datetime):
            return dt.replace(tzinfo=None)

        new_start = to_naive(time_log.start_time)
        new_end = to_naive(time_log.end_time)

        if new_start >= new_end:
            raise BadRequestError("Start time must be before end time")

        dayplan = self.repo.get_dayplanById(time_log.plan_id)
        if not dayplan:
            raise NotFoundError("DayPlan not found")

        for existing in dayplan.times:
            existing_start = to_naive(existing.start_time)
            existing_end = to_naive(existing.end_time)

            if new_start < existing_end and existing_start < new_end:
                raise BadRequestError("Time log overlaps with existing time log")

        task = self.task_repo.get_task(time_log.task_id)
        if not task:
            raise NotFoundError("Task not found")
        if task.owner_id != current_user.id:
            raise PermissionError("You don't have permission to work on this task")

        duration = self._Duration(time_log.start_time, time_log.end_time)
        task.done_hr += duration
        self.task_repo.update_task(task)

        # Pass the domain model directly to repository
        created_timelog = self.repo.create_time_log(time_log)
        return created_timelog  # domain model returned

    def delete_timelog(self, time_log_id: int, current_user):
        # You might want to verify ownership here before deleting
        time_log = self.repo.get_time_log(time_log_id)
        if not time_log:
            raise NotFoundError("Time log not found")
        if time_log.task.owner_id != current_user.id:
            raise PermissionError("You don't have permission to delete this time log")
        timelog = self.repo.deleteTimeLog(time_log_id)
        if not timelog:
            return None  # or raise NotFound error
        return timelog
