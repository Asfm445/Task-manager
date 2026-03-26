from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from domain.models.task_model import TaskCreateInput, TaskOutput, TaskProgressDomain


class AbstractTaskRepository(ABC):
    @abstractmethod
    async def get_task(self, task_id: int) -> Optional[TaskOutput]:
        pass

    @abstractmethod
    async def get_tasks(self, user_id: int, skip: int = 0, limit: Optional[int] = None, fetch_all: bool = False, search_name='',uncompleted=False,completed=False) -> List[TaskOutput]:
        pass

    @abstractmethod
    async def create_task(self, task: TaskCreateInput, owner_id: int) -> TaskOutput:
        pass

    @abstractmethod
    async def delete_task(self, task_id: int, owner_id: int) -> bool:
        pass

    @abstractmethod
    async def create_progress(self, progress: TaskProgressDomain) -> TaskProgressDomain:
        pass

    @abstractmethod
    async def assign_user_to_task(
        self, task_id: int, assignee_email: str
    ) -> Tuple[Optional[TaskOutput], Optional[str]]:
        """
        Returns (TaskOutput, None) on success, or (None, error_message) on failure.
        """
        pass

    @abstractmethod
    async def update_task(self, task_id: int, data: dict) -> Optional[TaskOutput]:
        """
        Returns (TaskOutput, None) on success, or (None, error_message) on failure.
        """
        pass

    @abstractmethod
    async def create_stop(self, task_id: int):
        pass

    @abstractmethod
    async def delete_stop(self, task_id: int):
        pass

    @abstractmethod
    async def get_stop(self, task_id: int):
        pass

    @abstractmethod
    async def get_progress(self, task_id: int, skip: int = 0, limit: int = 100):
        pass
    @abstractmethod
    async def get_tasks_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[TaskOutput]:
        pass
        
    @abstractmethod    
    async def get_assignees_of_task(self, task_id: int) -> List[int]:
        pass   

    @abstractmethod
    async def get_assignees_of_task_email(self, task_id: int) -> List[str]:
        pass

    @abstractmethod
    async def get_desription_and_id_of_subtasks(self, task_id: int) -> List[str]:
        pass
