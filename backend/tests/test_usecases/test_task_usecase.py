from datetime import datetime
from unittest.mock import ANY, MagicMock

import pytest
from api.schemas.schema import Task, TaskCreate
from domain.exceptions import BadRequestError, NotFoundError

# from domain.Models import TaskCreateInput, TaskOutput
from usecases.task_usecase import TaskService


class Test_get_task:

    def test_get_task_success(self):
        # Arrange
        mock_repo = MagicMock()
        service = TaskService(mock_repo)

        mock_user = MagicMock()
        mock_user.id = 1

        fake_task = MagicMock()
        fake_task.owner_id = 1
        fake_task.assignees = []

        mock_repo.get_task.return_value = fake_task

        # Act
        result = service.get_task(task_id=1, current_user=mock_user)

        # Assert
        assert result.id == fake_task.id
        mock_repo.get_task.assert_called_once_with(1)

    def test_get_task_not_found(self):
        mock_repo = MagicMock()
        service = TaskService(mock_repo)

        mock_user = MagicMock()
        mock_user.id = 1

        mock_repo.get_task.return_value = None

        with pytest.raises(NotFoundError):
            service.get_task(task_id=999, current_user=mock_user)

    def test_get_task_permission_denied(self):
        mock_repo = MagicMock()
        service = TaskService(mock_repo)

        mock_user = MagicMock()
        mock_user.id = 2

        fake_task = MagicMock()
        fake_task.owner_id = 1
        fake_task.assignees = []

        mock_repo.get_task.return_value = fake_task

        with pytest.raises(PermissionError):
            service.get_task(task_id=1, current_user=mock_user)


class Test_create_task:

    def test_create_task_success(self):
        mock_repo = MagicMock()
        service = TaskService(mock_repo)
        mock_user = MagicMock()
        mock_user.id = 1
        task_data = {
            "description": "newtask",
            "end_date": "2025-08-28T05:38:07.665Z",
            "estimated_hr": 20,
            "is_repititive": False,
            "status": "pending",
            "start_date": "2025-08-27T05:38:07.665Z",
            "main_task_id": None,
        }

        expected_data = {
            "description": "newtask",
            "end_date": datetime.fromisoformat("2025-08-28T22:38:07.665000"),
            "estimated_hr": 20.0,
            "is_repititive": False,
            "status": "pending",
            "start_date": datetime.fromisoformat("2025-08-26T22:38:07.665000"),
            "main_task_id": None,
            "id": 1,
            "subtasks": [],
            "assignees": [],
            "owner_id": 1,
        }
        mock_repo.create_task.return_value = Task(**expected_data)
        task = TaskCreate(**task_data)

        result = service.create_task(task=task, current_user=mock_user)
        assert result.__dict__ == expected_data
        mock_repo.create_task.assert_called_once_with(ANY)

    def test_create_task_with_main_task_not_found(self):
        mock_repo = MagicMock()
        service = TaskService(mock_repo)
        mock_user = MagicMock()
        mock_user.id = 1
        task_data = {
            "description": "newtask",
            "end_date": "2025-08-28T05:38:07.665Z",
            "estimated_hr": 20,
            "is_repititive": False,
            "status": "pending",
            "start_date": "2025-08-27T05:38:07.665Z",
            "main_task_id": 1,
        }
        mock_repo.get_task.return_value = None
        with pytest.raises(NotFoundError, match="Main task not found"):
            service.create_task(task=TaskCreate(**task_data), current_user=mock_user)

    def test_create_task_with_subtask_permission_denied(self):
        mock_repo = MagicMock()
        service = TaskService(mock_repo)
        mock_user = MagicMock()
        mock_user.id = 2
        task_data = {
            "description": "newtask",
            "end_date": "2025-08-28T05:38:07.665Z",
            "estimated_hr": 20,
            "is_repititive": False,
            "status": "pending",
            "start_date": "2025-08-27T05:38:07.665Z",
            "main_task_id": 1,
        }
        main_task = MagicMock()
        main_task.owner_id = 1
        mock_repo.get_task.return_value = main_task
        with pytest.raises(
            PermissionError, match="Cannot create subtask for another user's task"
        ):
            service.create_task(task=TaskCreate(**task_data), current_user=mock_user)

    def test_create_task_start_date_in_past(self):
        mock_repo = MagicMock()
        service = TaskService(mock_repo)
        mock_user = MagicMock()
        mock_user.id = 1
        task_data = {
            "description": "newtask",
            "end_date": "2025-08-28T05:38:07.665Z",
            "estimated_hr": 20,
            "is_repititive": False,
            "status": "pending",
            "start_date": "2023-08-27T05:38:07.665Z",  # Past date
            "main_task_id": None,
        }

        with pytest.raises(BadRequestError, match="Start date cannot be in the past"):
            service.create_task(task=TaskCreate(**task_data), current_user=mock_user)

    def test_create_task_end_date_before_start_date(self):
        mock_repo = MagicMock()
        service = TaskService(mock_repo)
        mock_user = MagicMock()
        mock_user.id = 1
        task_data = {
            "description": "newtask",
            "end_date": "2023-08-27T05:38:07.665Z",  # Before start date
            "estimated_hr": 20,
            "is_repititive": False,
            "status": "pending",
            "start_date": "2025-08-28T05:38:07.665Z",
            "main_task_id": None,
        }
        with pytest.raises(
            BadRequestError, match="End date cannot be before start date"
        ):
            service.create_task(task=TaskCreate(**task_data), current_user=mock_user)


class Test_get_tasks:

    def test_get_tasks_success(self):
        # Arrange
        mock_repo = MagicMock()
        service = TaskService(mock_repo)

        task1 = MagicMock()
        task1.id = 1
        task1.end_date = datetime(2025, 8, 28, 5, 38, 7, 665000)
        task1.start_date = datetime(2025, 8, 27, 5, 38, 7, 665000)
        task1.estimated_hr = 20
        task1.is_repititive = False
        task1.description = "newtask"
        task1.main_task_id = None
        task1.subtasks = []
        task1.status = "pending"
        task1.owner_id = 1
        task1.assignees = []

        task2 = MagicMock()

        task2.id = 2
        task2.end_date = datetime(2025, 8, 29, 5, 38, 7, 665000)
        task2.start_date = datetime(2025, 8, 28, 5, 38, 7, 665000)
        task2.estimated_hr = 20
        task2.is_repititive = False
        task2.description = "newtask2"
        task2.main_task_id = None
        task2.subtasks = []
        task2.status = "pending"
        task2.owner_id = 1
        task2.assignees = []

        task3 = MagicMock()
        task3.end_date = datetime(2025, 8, 30, 5, 38, 7, 665000)
        task3.start_date = datetime(2025, 8, 29, 5, 38, 7, 665000)
        task3.estimated_hr = 20
        task3.is_repititive = False
        task3.description = "newtask3"
        task3.main_task_id = None
        task3.subtasks = []
        task3.status = "pending"
        task3.id = 3
        task3.owner_id = 1
        task3.assignees = []

        mock_repo.get_tasks.return_value = [task1, task2, task3]
        current_user = MagicMock()
        current_user.id = 1

        # Act
        result = service.get_tasks(current_user)

        # Assert
        assert len(result) == 3
        assert result[0].id == 1
        assert result[1].id == 2
        assert result[2].id == 3

    def test_get_tasks_has_permission(self):
        # Arrange
        mock_repo = MagicMock()
        service = TaskService(mock_repo)
        user_assignee = MagicMock()
        user_assignee.id = 1
        user_assignee.email = "test@example.com"
        user_assignee.username = "testuser"
        user_assignee.my_tasks = []
        user_assignee.assigned_tasks = []

        task1 = MagicMock()
        task1.id = 1
        task1.end_date = datetime(2025, 8, 28, 5, 38, 7, 665000)
        task1.start_date = datetime(2025, 8, 27, 5, 38, 7, 665000)
        task1.estimated_hr = 20
        task1.is_repititive = False
        task1.description = "newtask"
        task1.main_task_id = None
        task1.subtasks = []
        task1.status = "pending"
        task1.owner_id = 1
        task1.assignees = []

        task2 = MagicMock()

        task2.id = 2
        task2.end_date = datetime(2025, 8, 29, 5, 38, 7, 665000)
        task2.start_date = datetime(2025, 8, 28, 5, 38, 7, 665000)
        task2.estimated_hr = 20
        task2.is_repititive = False
        task2.description = "newtask2"
        task2.main_task_id = None
        task2.subtasks = []
        task2.status = "pending"
        task2.owner_id = 2
        task2.assignees = []

        task3 = MagicMock()
        task3.end_date = datetime(2025, 8, 30, 5, 38, 7, 665000)
        task3.start_date = datetime(2025, 8, 29, 5, 38, 7, 665000)
        task3.estimated_hr = 20
        task3.is_repititive = False
        task3.description = "newtask3"
        task3.main_task_id = None
        task3.subtasks = []
        task3.status = "pending"
        task3.id = 3
        task3.owner_id = 2
        task3.assignees = [user_assignee]
        mock_repo.get_tasks.return_value = [task1, task2, task3]
        current_user = MagicMock()
        current_user.id = 1

        # Act
        result = service.get_tasks(current_user)

        # Assert
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 3
        assert result[1].id == 3
        assert result[1].id == 3
