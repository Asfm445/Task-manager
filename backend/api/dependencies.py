from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from infrastructure.db.session import AsyncSessionLocal
from infrastructure.repositories.dayplan_repository import DayPlanRepository
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.repositories.token_repository import TokenRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.services.jwt_service import JwtService
from infrastructure.services.password_service import PasswordService
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from usecases.dayplan_usecase import DayPlanUseCase
from usecases.task_usecase import TaskService
from usecases.user_usecase import UserUsecase
from infrastructure.uow.task_uow import SqlAlchemyUnitOfWork
from domain.repositories.iuow import IUnitOfWork
from infrastructure.uow.dayyplan_uow import DayPlanUnitOfWork
from domain.repositories.daypla_uow import IDayPlanUoW
# from api.config import settings
import os
from dotenv import load_dotenv


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
    password_service = PasswordService()
    return UserUsecase(repo, password_service, jwt_service, tokenRepo)




async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_usecase: UserUsecase = Depends(get_user_usecase),
):
    try:
        payload, err = user_usecase.jwt_service.decode_token(token)
        if not payload:
            raise HTTPException(status_code=400, detail=err)
        username = payload.get("username")
        email = payload.get("email")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    user = await user_usecase.getUserByEmail(email)  # must be async
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
