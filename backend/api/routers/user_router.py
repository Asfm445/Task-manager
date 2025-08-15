from api.dependencies import get_user_usecase
from api.schemas.user_schema import LoginInput, RefreshToken, UserCreate
from api.utilities.handle_service_result import handle_service_result
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/token")
@handle_service_result
async def login(user_info: LoginInput, usecase=Depends(get_user_usecase)):

    tokens = await usecase.Login(user_info)
    return tokens


@router.post("/register")
@handle_service_result
async def register_user(user: UserCreate, usecase=Depends(get_user_usecase)):
    return await usecase.Register(user)


@router.post(
    "/refresh",
)
@handle_service_result
async def refresh_token(token: RefreshToken, usecase=Depends(get_user_usecase)):
    return await usecase.RefreshToken(token.refresh_token)
