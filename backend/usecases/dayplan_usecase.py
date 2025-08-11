from datetime import date

from domain.Models import TimeLogCreate


class DayPlanUseCase:
    def __init__(self, repo):
        self.repo = repo

    def delete_dayplan(self, date: date, current_user):
        dayplan = self.repo.get_dayplan(date, current_user)
        if dayplan is not None:
            self.repo.delete_dayplan(date, current_user)
            return {"message": "Dayplan deleted successfully"}
        return False

    def get_dayplan(self, date: date, current_user):
        dayplan = self.repo.get_dayplan(date, current_user)
        if not dayplan:
            dayplan = self.repo.create_dayplan(date, current_user)
            return dayplan
        return dayplan

    def create_time_log(self, time_log: TimeLogCreate, plan_id: int, current_user):
        new_start = time_log.start_time
        new_end = time_log.end_time

        if new_start >= new_end:
            raise ValueError("Start time must be before end time")

        time_logs = self.repo.get_time_logs(plan_id, current_user.email)

        for existing in time_logs:
            if new_start < existing.end_time and existing.start_time < new_end:
                raise ValueError("Time log overlaps with existing time log")

        return self.repo.create_time_log(time_log.dict(), plan_id, current_user.email)
