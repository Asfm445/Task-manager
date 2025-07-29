# tests/services/test_task_service.py

# from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import MagicMock

import pytest

# from api.schemas.schema import Task  # Your output schema
from domain.exceptions import BadRequestError, NotFoundError
from services.task_service import TaskService


def test_get_task_success():
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
    assert result == fake_task
    mock_repo.get_task.assert_called_once_with(1)


def test_get_task_not_found():
    mock_repo = MagicMock()
    service = TaskService(mock_repo)

    mock_user = MagicMock()
    mock_user.id = 1

    mock_repo.get_task.return_value = None

    with pytest.raises(NotFoundError):
        service.get_task(task_id=999, current_user=mock_user)


def test_get_task_permission_denied():
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


def test_create_task_success():
    mock_repo = MagicMock()
    service = TaskService(mock_repo)
    mock_user = MagicMock()
    mock_user.id = 1
    task_data = {
        "description": "newtask",
        "end_date": "2025-07-28T05:38:07.665Z",
        "estimated_hr": 20,
        "is_repititive": False,
        "status": "pending",
        "start_date": "2025-07-27T05:38:07.665Z",
        "main_task_id": None,
    }
    
