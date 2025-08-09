from api.dependencies import get_user_usecase
from api.schemas.user_schema import LoginInput, RefreshToken, UserCreate
from api.utilities.handle_service_result import handle_service_result
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/token")
@handle_service_result
def login(user_info: LoginInput, usecase=Depends(get_user_usecase)):

    tokens = usecase.Login(user_info)
    return tokens


@router.post("/register")
@handle_service_result
def register_user(user: UserCreate, usecase=Depends(get_user_usecase)):
    return usecase.Register(user)


@router.post(
    "/refresh",
)
@handle_service_result
def refresh_token(token: RefreshToken, usecase=Depends(get_user_usecase)):
    return usecase.RefreshToken(token.refresh_token)
