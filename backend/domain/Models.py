from datetime import datetime
from enum import Enum
from typing import List, Optional


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskCreateInput:
    def __init__(
        self,
        description: str,
        end_date: datetime,
        estimated_hr: float,
        is_repititive: bool = False,
        status: TaskStatus = TaskStatus.pending,
        start_date: Optional[datetime] = None,
        main_task_id: Optional[int] = None,
    ):
        self.description = description
        self.end_date = end_date
        self.estimated_hr = estimated_hr
        self.is_repititive = is_repititive
        self.status = status
        self.start_date = start_date
        self.main_task_id = main_task_id


class TaskOutput(TaskCreateInput):
    def __init__(
        self,
        id: int,
        subtasks: Optional[List[int]] = None,
        assignees: Optional[List[int]] = None,
        owner_id: Optional[int] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.id = id
        self.subtasks = subtasks or []
        self.assignees = assignees or []
        self.owner_id = owner_id


# Domain model for user input (register)
class UserRegister:
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password


# Domain model for user (business layer)
class User:
    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        hashed_password: str,
        assigned_tasks=None,
        my_tasks=None,
    ):
        self.id = id
        self.hashed_password = hashed_password
        self.username = username
        self.email = email
        self.assigned_tasks = assigned_tasks or []
        self.my_tasks = my_tasks or []


# Conversion: from UserRegister to SQLAlchemy User mode


# Conversion: from SQLAlchemy UserModel to domain User


class UserLogin:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password


class Token:
    def __init__(
        self,
        id: str,
        token: str,
        user_id: int,
        created_at: datetime,
        expired_at: datetime,
    ):
        self.id = id
        self.token = token
        self.user_id = user_id
        self.created_at = created_at
        self.expired_at = expired_at
