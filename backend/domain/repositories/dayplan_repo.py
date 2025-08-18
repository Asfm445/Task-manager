from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from domain.models.dayplan_model import DayPlan, TimeLog

from .task_repo import AbstractTaskRepository


class AbstractDayPlanRepository(ABC):

    @abstractmethod
    def create_dayplan(self, date: date, current_user) -> DayPlan:
        pass

    @abstractmethod
    def get_dayplan(self, date: date, current_user) -> Optional[DayPlan]:
        pass

    @abstractmethod
    def get_dayplanById(self, id: int) -> Optional[DayPlan]:
        pass

    @abstractmethod
    def delete_dayplan(self, date: date, current_user) -> Optional[DayPlan]:
        pass

    @abstractmethod
    def deleteTimeLog(self, id: int) -> Optional[TimeLog]:
        pass

    @abstractmethod
    def create_time_log(self, time_log: TimeLog) -> TimeLog:
        pass

    @abstractmethod
    def get_time_log(self, id: int) -> Optional[TimeLog]:
        pass

    @abstractmethod
    async def update_time_log(self, time_log_id: int, data: dict)-> Optional[TimeLog]:
        pass
