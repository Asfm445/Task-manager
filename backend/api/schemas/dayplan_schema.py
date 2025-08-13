from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DayPlanBase(BaseModel):
    date: date


class DayPlanCreate(DayPlanBase):
    pass


class TimeBase(BaseModel):
    task_id: int
    start_time: time
    end_time: time
    plan_id: int


class TimeCreate(TimeBase):
    pass


class TaskDescription(BaseModel):
    description: str
    model_config = ConfigDict(from_attributes=True)


class Time(TimeBase):
    id: int
    done: bool
    task: Optional[TaskDescription]
    model_config = ConfigDict(from_attributes=True)


class DayPlan(DayPlanBase):
    id: int
    times: Optional[List[Time]] = []

    model_config = ConfigDict(from_attributes=True)
