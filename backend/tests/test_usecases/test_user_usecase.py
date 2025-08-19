# tests/services/test_task_service.py
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from domain.exceptions import BadRequestError, NotFoundError
from domain.Models import Token, User, UserLogin, UserRegister
from infrastructure.models.model import Token as dbToken
from usecases.user_usecase import UserUsecase


@pytest.mark.asyncio
async def test_user_register_success():
    mock_repo = AsyncMock()
    mock_pass_service = AsyncMock()
    mock_jwt_service = AsyncMock()
    mock_token_repo = AsyncMock()
    service = UserUsecase(
        mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo
    )
    user_data = {
        "username": "awel",
        "email": "awel@awel.com",
        "password": "1234",
    }
    mock_repo.FindByEmail.return_value = None
    mock_repo.FindByUsername.return_value = None
    mock_repo.Create.return_value = {"message": "User created successfully"}
    mock_pass_service.hash_password.return_value = "hashed_pass"

    result = await service.Register(UserRegister(**user_data))

    assert result["message"] == "User created successfully"

@pytest.mark.filterwarnings("ignore:coroutine 'AsyncMockMixin._execute_mock_call' was never awaited")
@pytest.mark.asyncio
async def test_user_register_email_exist():
    # Use AsyncMock for all async components
    mock_repo = AsyncMock()
    mock_pass_service = AsyncMock()  # Changed from MagicMock
    mock_jwt_service = AsyncMock()   # Changed from MagicMock
    mock_token_repo = AsyncMock()

    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo)

    user_data = {"username": "awel", "email": "awel@awel.com", "password": "1234"}
    user_expected = {"username": "awel", "email": "awel@awel.com", "hashed_password": "hashed_pass"}

    # Proper async mock setup
    mock_repo.FindByEmail = AsyncMock(return_value=User(1, **user_expected))

    with pytest.raises(BadRequestError, match="Email already exist"):
        await service.Register(UserRegister(**user_data))
    
    # await mock_repo.FindByEmail._awaitable_mock_call()
@pytest.mark.filterwarnings("ignore:coroutine 'AsyncMockMixin._execute_mock_call' was never awaited")
@pytest.mark.asyncio
async def test_login_success():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()   # JWT stays sync
    mock_token_repo = AsyncMock()
    service = UserUsecase(
        mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo
    )

    data = {"email": "awel@awel.com", "password": "1234"}
    user_expected = {"username": "awel", "email": "awel@awel.com", "hashed_password": "hashed_pass"}

    mock_repo.FindByEmail.return_value = User(1, **user_expected)
    mock_pass_service.verify_password.return_value = True
    mock_jwt_service.create_access_token.return_value = "access_token"
    mock_jwt_service.create_refresh_token.return_value = Token(
        1, "refresh_token", 1, datetime.now(), datetime.now()
    )
    mock_token_repo.Create.return_value = {"message": "Token created successfully"}

    result = await service.Login(UserLogin(**data))

    assert result["access_token"] == "access_token"
    assert result["refresh_token"] == "refresh_token"



@pytest.mark.asyncio
async def test_login_user_not_found():
    mock_repo = AsyncMock()
    mock_pass_service = AsyncMock()
    mock_jwt_service = AsyncMock()
    mock_token_repo = AsyncMock()
    service = UserUsecase(
        mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo
    )
    data = {"email": "awel@awel.com", "password": "1234"}
    mock_repo.FindByEmail.return_value = None

    with pytest.raises(NotFoundError, match="User not found"):
        await service.Login(UserLogin(**data))
    
    


@pytest.mark.asyncio
async def test_login_user_invalid_password():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo)

    data = {"email": "awel@awel.com", "password": "1234"}
    mock_repo.FindByEmail.return_value = User(
        1, username="awel", email="awel@awel.com", hashed_password="hashed_pass"
    )
    mock_pass_service.verify_password.return_value = False

    with pytest.raises(BadRequestError, match="Invalid password"):
        await service.Login(UserLogin(**data))




@pytest.mark.asyncio
async def test_refresh_token_success():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo)

    token = "valid_refresh_token"
    payload = {"id": "token-id-123", "user_id": 42}

    domain_token = MagicMock(token="hashedtoken")
    user = MagicMock(id=42, username="awel", email="awel@example.com")

    mock_jwt_service.decode_token.return_value = payload,None
    mock_token_repo.FindByID.return_value = [domain_token, user]
    mock_jwt_service.verify_token.return_value = True
    mock_jwt_service.create_access_token.return_value = "new_access_token"

    result = await service.RefreshToken(token)

    assert result == {"access_token": "new_access_token"}