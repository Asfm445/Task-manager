from api.dependencies import get_user_usecase, role_required
from api.dto.user_dto import user_create_to_domain, user_login_to_domain
from api.schemas.user_schema import (
    EmailRequest,
    LoginInput,
    NewPasswordRequest,
    RefreshToken,
    UserCreate,
)
from api.utilities.handle_service_result import handle_service_result
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/token")
@handle_service_result
async def login(user_info: LoginInput, usecase=Depends(get_user_usecase)):

    tokens = await usecase.Login(user_login_to_domain(user_info))
    return tokens


@router.post("/register")
@handle_service_result
async def register_user(user: UserCreate, usecase=Depends(get_user_usecase)):
    return await usecase.Register(user_create_to_domain(user))


@router.post(
    "/refresh",
)
@handle_service_result
async def refresh_token(token: RefreshToken, usecase=Depends(get_user_usecase)):
    return await usecase.RefreshToken(token.refresh_token)

@router.get("/verify-email")
@handle_service_result
async def verify_user(token:str, usecase=Depends(get_user_usecase)):
    return await usecase.VerifyEmail(token)

@router.post("/resend-verification")
@handle_service_result
async def resend_verification(email: EmailRequest, usecase=Depends(get_user_usecase)):
    return await usecase.SendVerification(email.email)

@router.post("/forgot-password")
@handle_service_result
async def forgot_password(email: EmailRequest, usecase=Depends(get_user_usecase)):
    return await usecase.SendPasswordReset(email.email)

@router.post("/reset-password")
@handle_service_result
async def reset_password(token:str, new_password: NewPasswordRequest, usecase=Depends(get_user_usecase)):
    return await usecase.ResetPassword(token, new_password.new_password)

@router.post("/promote")
@handle_service_result
async def Promote(email: EmailRequest, current_user=Depends(role_required(["superadmin"])),usecase=Depends(get_user_usecase)):
    return await usecase.Promote(email.email, current_user)

@router.post("/demote")
@handle_service_result
async def Demote(email: EmailRequest, current_user=Depends(role_required(["superadmin"])),usecase=Depends(get_user_usecase)):
    return await usecase.Demote(email.email, current_user)
