# infrastructure/uow.py
from domain.repositories.iuow import IUnitOfWork
from infrastructure.repositories.task_repository import TaskRepository
# from domain.repositories.task_repo import AbstractTaskRepository
# from sqlalchemy.ext.asyncio import AsyncSession

# infrastructure/uow.py
class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._session = None
        self._tasks = None
        
    @property
    def tasks(self):
        if self._tasks is None:
            self._session = self.session_factory()
            self._tasks = TaskRepository(self._session)
        return self._tasks
        
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