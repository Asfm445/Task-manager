from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from infrastructure.db.session import SessionLocal
from infrastructure.repositories.dayplan_repository import DayPlanRepository
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.repositories.token_repository import TokenRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.services.jwt_service import JwtService
from infrastructure.services.password_service import PasswordService
from jose import JWTError
from sqlalchemy.orm import Session
from usecases.dayplan_usecase import DayPlanUseCase

# from fastapi import Depends
from usecases.task_usecase import TaskService
from usecases.user_usecase import UserUsecase

SECRET_KEY = "allah_is_sufficient_for_us"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_HOURS = 24 * 7  # 7 days
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    repo = TaskRepository(db)
    return TaskService(repo)


def get_user_usecase(db: Session = Depends(get_db)) -> UserUsecase:
    repo = UserRepository(db)
    tokenRepo = TokenRepository(db)
    jwt_service = JwtService(
        SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_HOURS
    )
    password_service = PasswordService()
    return UserUsecase(repo, password_service, jwt_service, tokenRepo)


def get_dayplan_usecase(db: Session = Depends(get_db)) -> DayPlanUseCase:
    repo = DayPlanRepository(db)
    return DayPlanUseCase(repo)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_usecase: UserUsecase = Depends(
        get_user_usecase
    ),  # or Depends(get_user_usecase)
):
    try:
        payload, err = user_usecase.jwt_service.decode_token(
            token
        )  # calls JwtService internally
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

    user = user_usecase.getUserByEmail(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
