# tests/services/test_task_service.py

# from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from domain.exceptions import BadRequestError
from domain.Models import User, UserRegister
from services.user_sevice import UserService


def test_user_register_success():
    mock_repo = MagicMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    service = UserService(mock_repo, mock_pass_service, mock_jwt_service)
    user_data = {
        "username": "awel",
        "email": "awel@awel.com",
        "password": "1234",
    }
    user_expected = {
        "username": "awel",
        "email": "awel@awel.com",
        "password": "hashed_pass",
    }
    mock_repo.FindByEmail.return_value = None
    mock_repo.Create.return_value = User(1, **user_expected)
    mock_pass_service.hash_password.return_value = "hashed_pass"
    result = service.Register(UserRegister(**user_data))

    assert result.password == "hashed_pass"
    assert result.username == "awel"


def test_user_register_email_exist():
    mock_repo = MagicMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    service = UserService(mock_repo, mock_pass_service, mock_jwt_service)
    user_data = {
        "username": "awel",
        "email": "awel@awel.com",
        "password": "1234",
    }
    user_expected = {
        "username": "awel",
        "email": "awel@awel.com",
        "password": "hashed_pass",
    }

    mock_repo.FindByEmail.return_value = User(1, **user_expected)
    with pytest.raises(BadRequestError, match="Email already exist"):
        service.Register(UserRegister(**user_data))
