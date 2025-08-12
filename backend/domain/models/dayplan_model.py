from dataclasses import dataclass
from datetime import date, time
from typing import List, Optional

from domain.models.task_model import TaskOutput


@dataclass
class DayPlan:
    id: Optional[int]
    date: date
    user_id: int
    times: List["TimeLog"]  # forward reference


@dataclass
class TimeLogCreate:
    task_id: int
    start_time: time
    end_time: time
    plan_id: int


@dataclass
class TimeLog(TimeLogCreate):
    id: int
    task: "TaskOutput"
