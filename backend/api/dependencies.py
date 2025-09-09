# from api.config import settings
import os
from typing import List

from domain.interfaces.daypla_uow import IDayPlanUoW
from domain.interfaces.iuow import IUnitOfWork
from domain.models.user_model import TokenClaimUser
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from infrastructure.db.session import AsyncSessionLocal
from infrastructure.repositories.token_repository import TokenRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.services.email_service import EmailService
from infrastructure.services.jwt_service import JwtService
from infrastructure.services.password_service import PasswordService
from infrastructure.uow.dayyplan_uow import DayPlanUnitOfWork
from infrastructure.uow.task_uow import SqlAlchemyUnitOfWork
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from usecases.dayplan_usecase import DayPlanUseCase
from usecases.task_usecase import TaskService
from usecases.user_usecase import UserUsecase

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_HOURS = int(os.getenv("REFRESH_TOKEN_EXPIRE_HOURS"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")




# Async DB dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as db:
        yield db




async def get_dayplan_uow(db: AsyncSession = Depends(get_db)) -> IDayPlanUoW:
    return DayPlanUnitOfWork(lambda: db)

async def get_dayplan_usecase(uow: IDayPlanUoW = Depends(get_dayplan_uow)) -> DayPlanUseCase:
    return DayPlanUseCase(uow)

async def get_uow(db: AsyncSession = Depends(get_db)) -> IUnitOfWork:
    # Create a session factory that reuses the existing session
    return SqlAlchemyUnitOfWork(lambda: db)

async def get_task_service(uow: IUnitOfWork = Depends(get_uow)) -> TaskService:
    return TaskService(uow)


async def get_user_usecase(db: AsyncSession = Depends(get_db)) -> UserUsecase:
    repo = UserRepository(db)
    tokenRepo = TokenRepository(db)
    jwt_service = JwtService(
        SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_HOURS
    )
    email_service=EmailService()

    password_service = PasswordService()
    return UserUsecase(repo, password_service, jwt_service, tokenRepo, email_service)




async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_usecase: UserUsecase = Depends(get_user_usecase),
) -> TokenClaimUser:
    try:
        payload, err = user_usecase.jwt_service.decode_token(token)
        if not payload:
            raise HTTPException(status_code=400, detail=err)
        username = payload.get("username")
        email = payload.get("email")
        user_id = payload.get("user_id")
        role=payload.get("role")
        if username is None or email is None or user_id is None or role is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentialsss"
            )
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    return TokenClaimUser(user_id, email, username, role)


def role_required(permitted_roles: List[str]):
    async def _role_checker(
        current_user=Depends(get_current_user),
    ):
        if current_user.role not in permitted_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action",
            )
        return current_user
    return _role_checker
