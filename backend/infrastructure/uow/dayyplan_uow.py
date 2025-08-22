
from domain.interfaces.daypla_uow import IDayPlanUoW
from infrastructure.repositories.dayplan_repository import DayPlanRepository
from infrastructure.repositories.task_repository import TaskRepository


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
