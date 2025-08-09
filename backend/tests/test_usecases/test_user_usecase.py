# tests/services/test_task_service.py

# from datetime import datetime, timedelta
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from domain.exceptions import BadRequestError, NotFoundError
from domain.Models import Token, User, UserLogin, UserRegister
from infrastructure.models.model import Token as dbToken
from usecases.user_usecase import UserService


def test_user_register_success():
    mock_repo = MagicMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = MagicMock()
    service = UserService(
        mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo
    )
    user_data = {
        "username": "awel",
        "email": "awel@awel.com",
        "password": "1234",
    }
    mock_repo.FindByEmail.return_value = None
    mock_repo.Create.return_value = {"message": "User created successfully"}
    mock_pass_service.hash_password.return_value = "hashed_pass"
    result = service.Register(UserRegister(**user_data))
    print(result)
    assert result["message"] == "User created successfully"


def test_user_register_email_exist():
    mock_repo = MagicMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = MagicMock()
    service = UserService(
        mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo
    )
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


def test_login_success():
    mock_repo = MagicMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = MagicMock()
    service = UserService(
        mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo
    )
    data = {"email": "awel@awel.com", "password": "1234"}
    user_expected = {
        "username": "awel",
        "email": "awel@awel.com",
        "password": "hashed_pass",
    }
    mock_repo.FindByEmail.return_value = User(1, **user_expected)
    mock_pass_service.verify_password.return_value = True
    mock_jwt_service.create_access_token.return_value = "access_token"
    mock_jwt_service.create_refresh_token.return_value = Token(
        1, "refresh_token", 1, datetime.now(), datetime.now()
    )
    mock_token_repo.Create.return_value = {"message": "Token created successfully"}
    result = service.Login(UserLogin(**data))
    assert result["access_token"] == "access_token"
    assert result["refresh_token"] == "refresh_token"


def test_login_user_not_found():
    mock_repo = MagicMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = MagicMock()
    service = UserService(
        mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo
    )
    data = {"email": "awel@awel.com", "password": "1234"}
    mock_repo.FindByEmail.return_value = None
    with pytest.raises(NotFoundError, match="User not found"):
        service.Login(UserLogin(**data))


def test_login_user_invalid_password():
    mock_repo = MagicMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = MagicMock()
    service = UserService(
        mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo
    )
    data = {"email": "awel@awel.com", "password": "1234"}
    mock_repo.FindByEmail.return_value = User(
        1, username="awel", email="awel@awel.com", password="hashed_pass"
    )
    mock_pass_service.verify_password.return_value = False
    with pytest.raises(BadRequestError, match="Invalid password"):
        service.Login(UserLogin(**data))


def test_refresh_token_success():
    mock_repo = MagicMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = MagicMock()
    service = UserService(
        mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo
    )

    token = "valid_refresh_token"
    payload = {"id": "token-id-123", "user_id": 42}

    # Mock domain Token and User objects returned by tokenRepo.FindByID
    domain_token = MagicMock(token="hashedtoken")
    user = MagicMock(id=42, username="awel", email="awel@example.com")

    # Setup mocks for JwtService and TokenRepo
    mock_jwt_service.decode_token.return_value = payload
    mock_token_repo.FindByID.return_value = [domain_token, user]
    mock_jwt_service.verify_token.return_value = True
    mock_jwt_service.create_access_token.return_value = "new_access_token"

    result = service.RefreshToken(token)

    assert result == {"access_token": "new_access_token"}
