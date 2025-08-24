from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    stopped = "stopped"


class TaskBase(BaseModel):
    description: str
    end_date: datetime
    estimated_hr: float
    is_repititive: Optional[bool ]= False
    status: TaskStatus = TaskStatus.pending
    start_date: Optional[datetime] = None
    main_task_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    done_hr: float
    is_stopped: bool = False
    subtasks: Optional[List[int]] = []
    assignees: Optional[List[int]] = []
    owner_id: Optional[int] = None  # <-- Add this

    model_config = ConfigDict(from_attributes=True)


class AssignUserInput(BaseModel):
    assignee_email: EmailStr


class TaskUpdate(BaseModel):
    description: Optional[str] = None
    end_date: Optional[datetime] = None
    estimated_hr: Optional[int] = None
    is_repititive: Optional[bool] = None
    status: Optional[TaskStatus] = None
    start_date: Optional[datetime] = None
    main_task_id: Optional[int] = None


class TaskProgress(BaseModel):
    task_id: int
    start_date: datetime
    end_date: datetime
    status: TaskStatus
    done_hr: float
    estimated_hr: float
