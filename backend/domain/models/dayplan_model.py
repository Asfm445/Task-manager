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
    description: Optional[str] = None


@dataclass
class TimeLog:
    id: int
    task_id: int
    start_time: time
    end_time: time
    plan_id: int
    done: bool
    task: "TaskOutput"
    description: Optional[str] = None


@dataclass
class TaskAndTimeLogs:
    task_description: str
    time_logs: List[DayPlan]
    task_start_date: date
    task_end_date: date
    task_estimated_hr: float
    task_done_hr: float
    task_completion_rate: float

@dataclass
class AiRecommendation:
    feedback: str
    recommendations: str
    
