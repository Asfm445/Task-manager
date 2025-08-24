from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    stopped = "stopped"


@dataclass
class TaskCreateInput:
    description: str
    end_date: datetime
    estimated_hr: float
    is_repititive: bool = False
    is_stopped: bool = False
    done_hr: float = 0.0
    status: TaskStatus = TaskStatus.pending
    start_date: Optional[datetime] = None
    main_task_id: Optional[int] = None


@dataclass
class TaskOutput:
    id: int
    description: str
    end_date: datetime
    estimated_hr: float
    owner_id: int
    is_repititive: bool = False
    is_stopped: bool = False
    done_hr: float = 0.0
    status: TaskStatus = TaskStatus.pending
    start_date: Optional[datetime] = None
    main_task_id: Optional[int] = None
    subtasks: List[int] = field(default_factory=list)
    assignees: List[int] = field(default_factory=list)
    

@dataclass
class TimeTask:
    id: int
    description: str
    end_date: datetime
    estimated_hr: float
    owner_id: int
    is_repititive: bool = False
    is_stopped: bool = False
    done_hr: float = 0.0
    status: TaskStatus = TaskStatus.pending
    start_date: Optional[datetime] = None
    main_task_id: Optional[int] = None




@dataclass
class TaskUpdateInput:
    description: Optional[str] = None
    end_date: Optional[datetime] = None
    estimated_hr: Optional[float] = None
    is_repititive: Optional[bool] = None
    status: Optional[TaskStatus] = None
    start_date: Optional[datetime] = None
    main_task_id: Optional[int] = None


@dataclass
class TaskProgressDomain:
    task_id: int
    start_date: datetime
    end_date: datetime
    status: TaskStatus
    done_hr: float
    estimated_hr: float
