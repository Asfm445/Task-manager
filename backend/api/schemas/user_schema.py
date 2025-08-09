from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    assigned_tasks: Optional[List[int]] = []
    my_tasks: Optional[List[int]] = []

    model_config = ConfigDict(from_attributes=True)


class TaskProgressBase(BaseModel):
    start_date: datetime
    end_date: datetime
    task_id: int
    status: str
    done_hr: float
    estimated_hr: float


class TaskProgressCreate(TaskProgressBase):
    pass


class TaskProgress(TaskProgressBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class RefreshToken(BaseModel):
    refresh_token: str
