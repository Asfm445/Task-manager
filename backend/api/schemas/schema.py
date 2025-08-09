from datetime import datetime, time
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    stopped = "stopped"


class TaskBase(BaseModel):
    description: str
    end_date: datetime
    estimated_hr: float
    is_repititive: bool = False
    status: TaskStatus = TaskStatus.pending
    start_date: Optional[datetime] = None
    main_task_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    subtasks: Optional[List[int]] = []
    assignees: Optional[List[int]] = []
    owner_id: Optional[int] = None  # <-- Add this

    model_config = ConfigDict(from_attributes=True)


class DayPlanBase(BaseModel):
    date: datetime


class DayPlanCreate(DayPlanBase):
    pass


class DayPlan(DayPlanBase):
    id: int
    times: Optional[List[int]] = []

    model_config = ConfigDict(from_attributes=True)


class TimeBase(BaseModel):
    task_id: int
    start_time: time
    end_time: time
    plan_id: int

    @field_validator("end_time")
    def end_after_start(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class TimeCreate(TimeBase):
    pass


class Time(TimeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AssignUserInput(BaseModel):
    assignee_email: EmailStr
