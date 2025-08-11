from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class DayPlanBase(BaseModel):
    date: date


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
