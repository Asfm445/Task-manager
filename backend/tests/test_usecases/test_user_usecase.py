# tests/services/test_task_service.py

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from domain.exceptions import BadRequestError, NotFoundError
from domain.models.user_model import (
    Token,
    TokenClaimUser,
    User,
    UserLogin,
    UserRegister,
)
from usecases.user_usecase import UserUsecase


@pytest.mark.asyncio
async def test_user_register_success():
    # Mock all dependencies
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()

    # Instantiate the use case with mocks
    service = UserUsecase(
        mock_repo,
        mock_pass_service,
        mock_jwt_service,
        mock_token_repo,
        mock_email_service,
    )

    # Input data
    user_data = {
        "username": "awel",
        "email": "awel@awel.com",
        "password": "1234",
    }

    # Setup async return values
    mock_repo.FindByEmail.return_value = None
    mock_repo.FindByUsername.return_value = None
    mock_repo.get_all_users.return_value = []  # First user => superadmin
    mock_repo.Create.return_value = AsyncMock(id=1)  # async user creation
    mock_pass_service.hash_password.return_value = "hashed_pass"
    mock_jwt_service.create_verification_token.return_value = {"token": "rawtoken"}
    mock_jwt_service.hash_token.return_value = "hashedtoken"
    mock_email_service.send_verification_email = AsyncMock(return_value=True)
    mock_token_repo.Create = AsyncMock(return_value={"token": "token created successfully"})

    # Call the method
    result = await service.Register(UserRegister(**user_data))

    # Assert result
    assert result["message"] == "user registered successfully"


@pytest.mark.asyncio
async def test_user_register_with_invalid_email():
    # Mock all dependencies
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()

    # Instantiate the use case with mocks
    service = UserUsecase(
        mock_repo,
        mock_pass_service,
        mock_jwt_service,
        mock_token_repo,
        mock_email_service,
    )

    # Input data
    user_data = {
        "username": "awel",
        "email": "awel@awel.com",
        "password": "1234",
    }

    # Setup async return values
    mock_repo.FindByEmail.return_value = None
    mock_repo.FindByUsername.return_value = None
    mock_repo.get_all_users.return_value = []  # First user => superadmin
    mock_repo.Create.return_value = AsyncMock(id=1)  # async user creation
    mock_pass_service.hash_password.return_value = "hashed_pass"
    mock_jwt_service.create_verification_token.return_value = {"token": "rawtoken"}
    mock_jwt_service.hash_token.return_value = "hashedtoken"
    mock_email_service.send_verification_email = AsyncMock(return_value=False)
    mock_token_repo.Create.return_value = AsyncMock(return_value={"token": "token created successfully"})

    # Call the method
    with pytest.raises(BadRequestError): # result= await service.Register(UserRegister(**user_data))

    # Assert result
    # assert result["message"] == "user registered successfully"
        await service.Register(UserRegister(**user_data))
    mock_repo.Create.assert_not_awaited()
    mock_token_repo.Create.assert_not_awaited()

# @pytest.mark.filterwarnings("ignore:coroutine 'AsyncMockMixin._execute_mock_call' was never awaited")
@pytest.mark.asyncio
async def test_user_register_email_exist():
    # Use AsyncMock for all async components
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()  # Changed from MagicMock
    mock_jwt_service = MagicMock()  # Changed from MagicMock
    mock_token_repo = AsyncMock()
    mock_email_service= AsyncMock()

    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    user_data = {"username": "awel", "email": "awel@awel.com", "password": "1234"}
    user_expected = {"username": "awel", "email": "awel@awel.com", "hashed_password": "hashed_pass","verified":True, "role":"user"}

    # Proper async mock setup
    mock_repo.FindByEmail = AsyncMock(return_value=User(1, **user_expected))

    with pytest.raises(BadRequestError, match="Email already exist"):
        await service.Register(UserRegister(**user_data))
    
    
# @pytest.mark.filterwarnings("ignore:coroutine 'AsyncMockMixin._execute_mock_call' was never awaited")
@pytest.mark.asyncio
async def test_login_success():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()   # JWT stays sync
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(
        mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service
    )

    data = {"email": "awel@awel.com", "password": "1234"}
    user_expected = {"username": "awel", "email": "awel@awel.com", "hashed_password": "hashed_pass","verified":True, "role":"user"}

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
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(
        mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo,  mock_email_service
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
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    data = {"email": "awel@awel.com", "password": "1234"}
    mock_repo.FindByEmail.return_value = User(
        1, username="awel", email="awel@awel.com", hashed_password="hashed_pass",verified=True, role="user"
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
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    token = "valid_refresh_token"
    payload = {"id": "token-id-123", "user_id": 42}

    domain_token = MagicMock(token="hashedtoken")
    user = MagicMock(id=42, username="awel", email="awel@example.com")

    mock_jwt_service.decode_token.return_value = payload, None
    mock_token_repo.FindByID.return_value = [domain_token, user]
    mock_jwt_service.verify_token.return_value = True
    mock_jwt_service.create_access_token.return_value = "new_access_token"
    mock_token_repo.DeleteByID.return_value = None
    mock_token_repo.Create.return_value = None
    mock_jwt_service.create_refresh_token.return_value = Token(
        1, "refresh_token", 1, datetime.now(), datetime.now()
    )

    result = await service.RefreshToken(token)

    assert result == {"access_token": "new_access_token","refresh_token":"refresh_token","token_type": "bearer"}

# Additional test cases for missing functionality

@pytest.mark.asyncio
async def test_refresh_token_invalid_token():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    token = "invalid_token"
    mock_jwt_service.decode_token.return_value = None, "Invalid token"

    with pytest.raises(BadRequestError, match="Invalid token"):
        await service.RefreshToken(token)

@pytest.mark.asyncio
async def test_refresh_token_token_not_found():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    token = "valid_token"
    payload = {"id": "token-id-123", "user_id": 42}
    
    mock_jwt_service.decode_token.return_value = payload, None
    mock_token_repo.FindByID.return_value = None

    with pytest.raises(BadRequestError, match="Invalid token"):
        await service.RefreshToken(token)

@pytest.mark.asyncio
async def test_refresh_token_token_user_mismatch():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    token = "valid_token"
    payload = {"id": "token-id-123", "user_id": 42}
    
    domain_token = MagicMock(token="hashedtoken")
    user = MagicMock(id=999, username="awel", email="awel@example.com")  # Different user ID
    
    mock_jwt_service.decode_token.return_value = payload, None
    mock_token_repo.FindByID.return_value = [domain_token, user]
    mock_jwt_service.verify_token.return_value = True

    with pytest.raises(BadRequestError, match="Token-user mismatch"):
        await service.RefreshToken(token)

@pytest.mark.asyncio
async def test_verify_email_success():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    token = "valid_verification_token"
    payload = {"id": "token-id-123"}
    
    domain_token = MagicMock(token="hashedtoken", user_id=42)
    user = MagicMock(id=42, username="awel", email="awel@example.com")
    
    mock_jwt_service.decode_token.return_value = payload, None
    mock_token_repo.FindByID = AsyncMock(return_value=[domain_token, user])
    mock_jwt_service.verify_token.return_value = True
    mock_repo.update_user = AsyncMock()
    mock_token_repo.DeleteByID = AsyncMock()

    result = await service.VerifyEmail(token)

    assert result["message"] == "user verified successfully"
    mock_repo.update_user.assert_awaited_once_with(42, verified=True)
    # mock_token_repo.DeleteByID.assert_awaited_once_with("token-id-123")

@pytest.mark.asyncio
async def test_verify_email_invalid_token():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    token = "invalid_token"
    mock_jwt_service.decode_token.return_value = None, "Invalid token"

    with pytest.raises(BadRequestError, match="Invalid token"):
        await service.VerifyEmail(token)

@pytest.mark.asyncio
async def test_send_verification_success():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "awel@example.com"
    user = User(1, username="awel", email=email, verified=False, role="user", hashed_password="hashed")
    
    mock_repo.FindByEmail.return_value = user
    mock_jwt_service.create_verification_token.return_value = {"token": "rawtoken"}
    mock_jwt_service.hash_token.return_value = "hashedtoken"
    mock_email_service.send_verification_email = AsyncMock(return_value=True)
    mock_token_repo.Create = AsyncMock()

    result = await service.SendVerification(email)

    assert result["message"] == "email verification sent"
    mock_email_service.send_verification_email.assert_awaited_once()

@pytest.mark.asyncio
async def test_send_verification_user_not_found():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "nonexistent@example.com"
    mock_repo.FindByEmail.return_value = None

    with pytest.raises(NotFoundError, match="User Not Found"):
        await service.SendVerification(email)

@pytest.mark.asyncio
async def test_send_verification_already_verified():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "awel@example.com"
    user = User(1, username="awel", email=email, verified=True, role="user", hashed_password="hashed")
    
    mock_repo.FindByEmail.return_value = user

    result = await service.SendVerification(email)

    assert result["message"] == "you are verifed already!"

@pytest.mark.asyncio
async def test_send_password_reset_success():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "awel@example.com"
    user = User(1, username="awel", email=email, verified=True, role="user", hashed_password="hashed")
    
    mock_repo.FindByEmail.return_value = user
    mock_jwt_service.create_verification_token.return_value = {"token": "rawtoken"}
    mock_jwt_service.hash_token.return_value = "hashedtoken"
    mock_email_service.send_password_reset_email = AsyncMock(return_value=True)
    mock_token_repo.Create = AsyncMock()

    result = await service.SendPasswordReset(email)

    assert result["message"] == "password reset sent"
    mock_email_service.send_password_reset_email.assert_awaited_once()

@pytest.mark.asyncio
async def test_send_password_reset_user_not_found():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "nonexistent@example.com"
    mock_repo.FindByEmail.return_value = None

    with pytest.raises(NotFoundError, match="User Not Found"):
        await service.SendPasswordReset(email)

@pytest.mark.asyncio
async def test_reset_password_success():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    token = "valid_reset_token"
    new_password = "newpassword123"
    payload = {"id": "token-id-123"}
    
    domain_token = MagicMock(token="hashedtoken", user_id=42)
    user = MagicMock(id=42, username="awel", email="awel@example.com")
    
    mock_jwt_service.decode_token.return_value = payload, None
    mock_token_repo.FindByID.return_value = [domain_token, user]
    mock_jwt_service.verify_token.return_value = True
    mock_pass_service.hash_password.return_value = "new_hashed_password"
    mock_repo.update_user = AsyncMock()
    mock_token_repo.DeleteByID = AsyncMock()

    result = await service.ResetPassword(token, new_password)

    assert result["message"] == "password changed successfully"
    mock_pass_service.hash_password.assert_called_once_with(new_password)
    mock_repo.update_user.assert_awaited_once_with(42, hashed_password="new_hashed_password")
    # mock_token_repo.DeleteByID.assert_awaited_once_with("token-id-123")

@pytest.mark.asyncio
async def test_reset_password_invalid_token():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    token = "invalid_token"
    new_password = "newpassword123"
    mock_jwt_service.decode_token.return_value = None, "Invalid token"

    with pytest.raises(BadRequestError, match="Invalid token"):
        await service.ResetPassword(token, new_password)

@pytest.mark.asyncio
async def test_get_user_by_email_success():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "awel@example.com"
    user = User(1, username="awel", email=email, verified=True, role="user", hashed_password="hashed")
    
    mock_repo.FindByEmail.return_value = user

    result = await service.getUserByEmail(email)

    assert result == user
    mock_repo.FindByEmail.assert_awaited_once_with(email)

@pytest.mark.asyncio
async def test_get_user_by_email_not_found():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "nonexistent@example.com"
    mock_repo.FindByEmail.return_value = None

    with pytest.raises(NotFoundError, match="User not found"):
        await service.getUserByEmail(email)

@pytest.mark.asyncio
async def test_promote_user_success():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "user@example.com"
    current_user = TokenClaimUser(id=1, email="admin@example.com", username="admin", role="superadmin")
    user = User(2, username="user", email=email, verified=True, role="user", hashed_password="hashed")
    
    mock_repo.FindByEmail.return_value = user
    mock_repo.update_user = AsyncMock()

    result = await service.Promote(email, current_user)

    assert result["message"] == "user promoted successfully"
    mock_repo.update_user.assert_awaited_once_with(2, role="admin")

@pytest.mark.asyncio
async def test_promote_user_not_found():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "nonexistent@example.com"
    current_user = TokenClaimUser(id=1, email="admin@example.com", username="admin", role="superadmin")
    
    mock_repo.FindByEmail.return_value = None

    with pytest.raises(NotFoundError, match="User not found"):
        await service.Promote(email, current_user)

@pytest.mark.asyncio
async def test_promote_user_insufficient_permission():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "user@example.com"
    current_user = TokenClaimUser(id=1, email="user@example.com", username="user", role="user")  # Not superadmin
    user = User(2, username="admin", email=email, verified=True, role="admin", hashed_password="hashed")
    
    mock_repo.FindByEmail.return_value = user

    with pytest.raises(PermissionError, match="insufficient permission"):
        await service.Promote(email, current_user)

@pytest.mark.asyncio
async def test_promote_admin_user():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "admin@example.com"
    current_user = TokenClaimUser(id=1, email="superadmin@example.com", username="superadmin", role="superadmin")
    user = User(2, username="admin", email=email, verified=True, role="admin", hashed_password="hashed")  # Already admin
    
    mock_repo.FindByEmail.return_value = user

    with pytest.raises(PermissionError, match="insufficient permission"):
        await service.Promote(email, current_user)

@pytest.mark.asyncio
async def test_demote_user_success():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "admin@example.com"
    current_user = TokenClaimUser(id=1, email="superadmin@example.com", username="superadmin", role="superadmin")
    user = User(2, username="admin", email=email, verified=True, role="admin", hashed_password="hashed")
    
    mock_repo.FindByEmail.return_value = user
    mock_repo.update_user = AsyncMock()

    result = await service.Demote(email, current_user)

    assert result["message"] == "user demoted successfully"
    mock_repo.update_user.assert_awaited_once_with(2, role="user")

@pytest.mark.asyncio
async def test_demote_user_not_found():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "nonexistent@example.com"
    current_user = TokenClaimUser(id=1, email="superadmin@example.com", username="superadmin", role="superadmin")
    
    mock_repo.FindByEmail.return_value = None

    with pytest.raises(NotFoundError, match="User not found"):
        await service.Demote(email, current_user)

@pytest.mark.asyncio
async def test_demote_user_insufficient_permission():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    email = "admin@example.com"
    current_user = TokenClaimUser(id=1, email="user@example.com", username="user", role="user")  # Not superadmin
    user = User(2, username="admin", email=email, verified=True, role="admin", hashed_password="hashed")
    
    mock_repo.FindByEmail.return_value = user

    with pytest.raises(PermissionError, match="insufficient permission"):
        await service.Demote(email, current_user)



@pytest.mark.asyncio
async def test_login_user_not_verified():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    data = {"email": "awel@awel.com", "password": "1234"}
    user = User(1, username="awel", email="awel@awel.com", hashed_password="hashed_pass", verified=False, role="user")
    
    mock_repo.FindByEmail.return_value = user

    with pytest.raises(BadRequestError, match="Email not verified"):
        await service.Login(UserLogin(**data))

@pytest.mark.asyncio
async def test_user_register_username_exists():
    mock_repo = AsyncMock()
    mock_pass_service = MagicMock()
    mock_jwt_service = MagicMock()
    mock_token_repo = AsyncMock()
    mock_email_service = AsyncMock()
    service = UserUsecase(mock_repo, mock_pass_service, mock_jwt_service, mock_token_repo, mock_email_service)

    user_data = {"username": "awel", "email": "awel@awel.com", "password": "1234"}
    existing_user = User(1, username="awel", email="different@email.com", hashed_password="hashed_pass", verified=True, role="user")

    mock_repo.FindByEmail.return_value = None
    mock_repo.FindByUsername.return_value = existing_user

    with pytest.raises(BadRequestError, match="Username already exist"):
        await service.Register(UserRegister(**user_data))
