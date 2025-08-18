from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from domain.repositories.dayplan_repo import AbstractDayPlanRepository
from infrastructure.repositories.dayplan_repository import DayPlanRepository
from domain.repositories.daypla_uow import IDayPlanUoW
from infrastructure.repositories.task_repository import TaskRepository


# class DayPlanUnitOfWork(IDayPlanUoW):
#     def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
#         self.session_factory = session_factory
#         self._session: AsyncSession | None = None
#         self.dayplan_repo: DayPlanRepository | None = None
#         self.task_repo: TaskRepository | None = None

#     async def __aenter__(self):
#         self._session = self.session_factory()
#         self.dayplan_repo = DayPlanRepository(self._session)
#         self.task_repo = TaskRepository(self._session)
#         return self

#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         if exc_type:
#             await self.rollback()
#         await self._session.close()

#     async def commit(self):
#         if self._session:
#             await self._session.commit()

#     async def rollback(self):
#         if self._session:
#             await self._session.rollback()

#     @property
#     def session(self) -> AsyncSession:
#         if not self._session:
#             raise RuntimeError("Session not initialized. Use 'async with' context.")
#         return self._session


# # infrastructure/uow.py
# from domain.repositories.iuow import IUnitOfWork
# from infrastructure.repositories.task_repository import TaskRepository
# from domain.repositories.task_repo import AbstractTaskRepository
# from sqlalchemy.ext.asyncio import AsyncSession

# infrastructure/uow.py
class DayPlanUnitOfWork(IDayPlanUoW):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._session = None
        self._tasks = None
        self._dayplan=None
        
    @property
    def task_repo(self):
        if self._tasks is None:
            self._session = self.session_factory()
            self._dayplan = TaskRepository(self._session)
        return self._tasks
    
    @property
    def dayplan_repo(self):
        if self._dayplan is None:
            self._session = self.session_factory()
            self._dayplan = DayPlanRepository(self._session)
        return self._dayplan
    
        
    async def __aenter__(self):
        if self._session is None:
            self._session = self.session_factory()
            self._tasks = TaskRepository(self._session)
        if not self._session.in_transaction():
            await self._session.begin()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session is None:
            return
            
        try:
            if exc_type is None and self._session.in_transaction():
                await self._session.commit()
            elif self._session.in_transaction():
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None
            self._tasks = None
