from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

# class TaskStatus(str, Enum):
#     pending = "pending"
#     in_progress = "in_progress"
#     completed = "completed"
#     stopped = "stopped"


# @dataclass
# class TaskCreateInput:
#     description: str
#     end_date: datetime
#     estimated_hr: float
#     is_repititive: bool = False
#     status: TaskStatus = TaskStatus.pending
#     start_date: Optional[datetime] = None
#     main_task_id: Optional[int] = None


# @dataclass
# class TaskOutput(TaskCreateInput):
#     id: int
#     subtasks: List[int] = field(default_factory=list)
#     assignees: List[int] = field(default_factory=list)
#     owner_id: Optional[int] = None


@dataclass
class UserRegister:
    username: str
    email: str
    password: str


@dataclass
class User:
    id: int
    username: str
    email: str
    verified: bool
    role: str
    hashed_password: str
    assigned_tasks: List[int] = field(default_factory=list)
    my_tasks: List[int] = field(default_factory=list)


@dataclass
class UserLogin:
    email: str
    password: str


@dataclass
class Token:
    id: str
    token: str
    user_id: int
    created_at: datetime
    expired_at: datetime


@dataclass
class TokenClaimUser:
    id: int
    email: str
    username: str
    role: str
    

