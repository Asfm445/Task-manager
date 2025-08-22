from datetime import date, datetime, time

from domain.exceptions import BadRequestError, NotFoundError
from domain.interfaces.daypla_uow import IDayPlanUoW
from domain.models.dayplan_model import TimeLogCreate


class DayPlanUseCase:
    def __init__(
        self, uow: IDayPlanUoW
    ):
        self.uow=uow
    def _Duration(self, start_time: time, end_time: time) -> float:
        # Combine with a date so subtraction works
        start_dt = datetime.combine(date.today(), start_time)
        end_dt = datetime.combine(date.today(), end_time)
        delta = end_dt - start_dt
        return round(delta.total_seconds() / 3600, 2)

    async def delete_dayplan(self, date: date, current_user):
        async with self.uow:
            dayplan = await self.uow.dayplan_repo.get_dayplan(date, current_user)
            if not dayplan:
                raise NotFoundError("Dayplan not found")
            deleted_dayplan = await self.uow.dayplan_repo.delete_dayplan(date, current_user)
            return deleted_dayplan  # Return domain model for router response

    async def get_dayplan(self, date: date, current_user):
        async with self.uow:
            dayplan = await self.uow.dayplan_repo.get_dayplan(date, current_user)
            if not dayplan:
                dayplan = await self.uow.dayplan_repo.create_dayplan(date, current_user)
            return dayplan  # domain model returned

    async def create_time_log(self, time_log: TimeLogCreate, current_user):
        created_timelog=None
        async with self.uow:
            try:
                def to_naive(dt: datetime):
                    return dt.replace(tzinfo=None)

                new_start = to_naive(time_log.start_time)
                new_end = to_naive(time_log.end_time)

                if new_start >= new_end:
                    raise BadRequestError("Start time must be before end time")

                dayplan = await self.uow.dayplan_repo.get_dayplanById(time_log.plan_id)
                if not dayplan:
                    raise NotFoundError("DayPlan not found")

                for existing in dayplan.times:
                    existing_start = to_naive(existing.start_time)
                    existing_end = to_naive(existing.end_time)

                    if new_start < existing_end and existing_start < new_end:
                        raise BadRequestError("Time log overlaps with existing time log")

                task = await self.uow.task_repo.get_task(time_log.task_id)
                if not task:
                    raise NotFoundError("Task not found")
                if task.owner_id != current_user.id :
                    raise PermissionError("You don't have permission to work on this task")

                if task.status == "pending":
                    await self.uow.task_repo.update_task(task.id, {"status": "in_progress"})

                # Pass the domain model directly to repository
                created_timelog = await self.uow.dayplan_repo.create_time_log(time_log)
            except Exception:
                await self.uow.rollback()
                raise
            else:
                await self.uow.commit()
        return created_timelog  # domain model returned

    async def delete_timelog(self, time_log_id: int, current_user):
        async with self.uow:
            time_log = await self.uow.dayplan_repo.get_time_log(time_log_id)
            if not time_log:
                raise NotFoundError("Time log not found")
            if time_log.task.owner_id != current_user.id:
                raise PermissionError("You don't have permission to delete this time log")
            timelog = await self.uow.dayplan_repo.deleteTimeLog(time_log_id)
            if not timelog:
                raise NotFoundError("time log not found")
            return timelog

    async def mark_timelog_success(self, timelog_id: int, current_user):
        time_log=None
        async with self.uow:
            try:
                time_log = await self.uow.dayplan_repo.get_time_log(timelog_id)
                if not time_log:
                    raise NotFoundError("Time log not found")
                if time_log.task.owner_id != current_user.id:
                    raise PermissionError(
                        "You don't have permission to mark this time log as successful"
                    )
                if time_log.done:
                    raise BadRequestError("time log already done")
                
                time_log = await self.uow.dayplan_repo.update_time_log(time_log.id,{"done":True})
                

                duration = self._Duration(time_log.start_time, time_log.end_time)

                if not time_log:
                    raise NotFoundError("Time log not found")

                task = time_log.task
                task.done_hr += duration

                while task and task.done_hr >= task.estimated_hr:
                    data = {"done_hr": task.done_hr, "status": "completed"}
                    task = await self.uow.task_repo.update_task(task.id, data)
                    if not task:
                        raise BadRequestError("Task update failed")

                    if task.main_task_id:
                        sb_task_es_hr = task.estimated_hr
                        task = await self.uow.task_repo.get_task(task.main_task_id)
                        task.done_hr += sb_task_es_hr
                    else:
                        break
                else:
                    if task and task.status == "pending":
                        await self.uow.task_repo.update_task(
                            task.id, {"done_hr": task.done_hr, "status": "in_progress"}
                        )
            except Exception:
                await self.uow.rollback()
                raise
            else:
                await self.uow.commit()

        return time_log




