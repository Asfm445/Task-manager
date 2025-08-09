from schemas import schema


class TimeLogService:
    def __init__(self, repo):
        self.repo = repo

    def get_time_logs(self, plan_id: int, current_user):
        return self.repo.get_time_logs(plan_id, current_user.email)

    def create_time_log(
        self, time_log: schema.TimeLogCreate, plan_id: int, current_user
    ):
        new_start = time_log.start_time
        new_end = time_log.end_time

        if new_start >= new_end:
            raise ValueError("Start time must be before end time")

        time_logs = self.repo.get_time_logs(plan_id, current_user.email)

        for existing in time_logs:
            if new_start < existing.end_time and existing.start_time < new_end:
                raise ValueError("Time log overlaps with existing time log")

        return self.repo.create_time_log(time_log.dict(), plan_id, current_user.email)
