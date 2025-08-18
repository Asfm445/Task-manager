# from abc import ABC, abstractmethod
# from domain.repositories.dayplan_repo import AbstractDayPlanRepository
# from domain.repositories.task_repo import AbstractTaskRepository

# class IDayPlanUoW(ABC):
#     dayplan_repo: AbstractDayPlanRepository
#     task_repo: AbstractTaskRepository

#     @abstractmethod
#     async def __aenter__(self):
#         ...

#     @abstractmethod
#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         ...

#     @abstractmethod
#     async def commit(self):
#         ...

#     @abstractmethod
#     async def rollback(self):
#         ...

from typing import Protocol
from domain.repositories.task_repo import AbstractTaskRepository
from domain.repositories.dayplan_repo import AbstractDayPlanRepository

# domain/repositories/uow.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class IDayPlanUoW(Protocol):
    @property
    def task_repo(self) -> 'AbstractTaskRepository': ...
    @property
    def dayplan_repo(self) -> 'AbstractDayPlanRepository': ...
    
    async def __aenter__(self) -> 'IDayPlanUoW': ...
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...
    async def commit(self): ...
    async def rollback(self): ...