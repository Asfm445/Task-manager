from domain.exceptions import BadRequestError, NotFoundError
from domain.interfaces.email_service import EmailServiceInterface
from domain.interfaces.jwt_service import JwtServiceInterface
from domain.interfaces.password_service import IPasswordService
from domain.interfaces.token_repo import ITokenRepository
from domain.interfaces.user_repo import IUserRepository
from domain.models.user_model import TokenClaimUser, UserLogin, UserRegister


class UserUsecase:
    def __init__(self, repo: IUserRepository, pass_service: IPasswordService, jwt_service: JwtServiceInterface, tokenRepo: ITokenRepository, email_service: EmailServiceInterface):
        self.repo = repo
        self.pass_service = pass_service
        self.jwt_service = jwt_service
        self.tokenRepo = tokenRepo
        self.email_service=email_service

    async def Register(self, user: UserRegister):
        if await self.repo.FindByEmail(user.email):
            raise BadRequestError("Email already exist")
        if await self.repo.FindByUsername(user.username):
            raise BadRequestError("Username already exist")
        data={"username":user.username,"email":user.email}
        token=self.jwt_service.create_verification_token(data)
        result = await self.email_service.send_verification_email(user.username,user.email, token["token"])
        print(result)
        if not result:
            raise BadRequestError("invalid Email")
        token["token"]=self.jwt_service.hash_token(token["token"])
        hashed_password = self.pass_service.hash_password(user.password)
        result = await self.repo.get_all_users()
        if len(result)==0:
            role="superadmin"
        else:
            role="user"
        
        created_user=await self.repo.Create(user, hashed_password, role)
        token["user_id"]=created_user.id
            
        token=await self.tokenRepo.Create(token)
        return {"message":"user registered successfully"}
    
    async def SendVerification(self, email):
        user=await self.repo.FindByEmail(email)
        if not user:
            raise NotFoundError("User Not Found")
        if user.verified:
            return {"message": "you are verifed already!"}
        data={"username":user.username,"email":user.email}
        token=self.jwt_service.create_verification_token(data)
        result = await self.email_service.send_verification_email(user.username,user.email, token["token"])
        if not result:
            raise BadRequestError("invalid Email")
        token["token"]=self.jwt_service.hash_token(token["token"])
        token["user_id"]=user.id
        await self.tokenRepo.Create(token)

        return {"message": "email verification sent"}





    async def Login(self, user_info: UserLogin):
        user = await self.repo.FindByEmail(user_info.email)
        if not user:
            raise NotFoundError("User not found")
        if not user.verified:
            raise BadRequestError("Email not verified")
        if not self.pass_service.verify_password(
            user_info.password, user.hashed_password
        ):
            raise BadRequestError("Invalid password")

        access_token = self.jwt_service.create_access_token(
            data={"username": user.username, "email": user.email, "role":user.role, "user_id": user.id}
        )
        refresh_token = self.jwt_service.create_refresh_token(
            data={
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            }
        )
        tokenStr = refresh_token.token
        refresh_token.token = self.jwt_service.hash_token(tokenStr)
        await self.tokenRepo.Create(refresh_token.__dict__)

        return {
            "access_token": access_token,
            "refresh_token": tokenStr,
            "token_type": "bearer",
        }

    async def getUserByEmail(self, email):
        user = await self.repo.FindByEmail(email)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def RefreshToken(self, token):
        payload, err = self.jwt_service.decode_token(token)
        if not payload:
            raise BadRequestError(err)
        

        result = await self.tokenRepo.FindByID(payload["id"])
        if not result:
            raise BadRequestError("Invalid token")
        

        dbtoken, user = result
        if not self.jwt_service.verify_token(token, dbtoken.token):
            raise BadRequestError("Invalid token")

        # Optional extra check for stolen tokens
        if user.id != payload.get("user_id"):
            raise BadRequestError("Token-user mismatch")

        access_token = self.jwt_service.create_access_token(
            data={"username": user.username, "email": user.email, "role":user.role, "user_id": user.id}
        )
        refresh_token = self.jwt_service.create_refresh_token(
            data={
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            }
        )
        tokenStr = refresh_token.token
        refresh_token.token = self.jwt_service.hash_token(tokenStr)
        await self.tokenRepo.Create(refresh_token.__dict__)
        await self.tokenRepo.DeleteByID(dbtoken.id)

        return {
            "access_token": access_token,
            "refresh_token": tokenStr,
            "token_type": "bearer",
        }
    

    async def VerifyEmail(self,token: str):
        payload, err=self.jwt_service.decode_token(token)
        if not payload:
            raise BadRequestError(err)
        result = await self.tokenRepo.FindByID(payload["id"])
        if not result:
            raise BadRequestError("Invalid token")
        dbtoken, user = result
        if not self.jwt_service.verify_token(token, dbtoken.token):
            raise BadRequestError("Invalid token")

        # Optional extra check for stolen tokens
        if user.id != dbtoken.user_id:
            raise BadRequestError("Token-user mismatch")
        await self.repo.update_user(user.id, verified=True)
        await self.tokenRepo.DeleteByID(dbtoken.id)

        return {"message": "user verified successfully"}
    

    async def SendPasswordReset(self, email):
        user=await self.repo.FindByEmail(email)
        if not user:
            raise NotFoundError("User Not Found")

        data={"username":user.username,"email":user.email}
        token=self.jwt_service.create_verification_token(data)
        result = await self.email_service.send_password_reset_email(user.username,user.email, token["token"])
        if not result:
            raise BadRequestError("invalid Email")
        token["token"]=self.jwt_service.hash_token(token["token"])
        token["user_id"]=user.id
        await self.tokenRepo.Create(token)

        return {"message": "password reset sent"}
    
    async def ResetPassword(self,token: str, newpassword: str):
        payload, err=self.jwt_service.decode_token(token)
        if not payload:
            raise BadRequestError(err)
        result = await self.tokenRepo.FindByID(payload["id"])
        if not result:
            raise BadRequestError("Invalid token")
        dbtoken, user = result
        if not self.jwt_service.verify_token(token, dbtoken.token):
            raise BadRequestError("Invalid token")

        # Optional extra check for stolen tokens
        if user.id != dbtoken.user_id:
            raise BadRequestError("Token-user mismatch")
        hashed_password=self.pass_service.hash_password(newpassword)
        await self.repo.update_user(user.id, hashed_password=hashed_password)
        await self.tokenRepo.DeleteByID(dbtoken.id)

        return {"message": "password changed successfully"}
    
    async def Promote(self,email: str, current_user: TokenClaimUser):
        user=await self.repo.FindByEmail(email)
        if not user:
            raise NotFoundError("User not found")
        if current_user.role!="superadmin" or user.role!="user":
            raise PermissionError("insufficient permission")
        
        await self.repo.update_user(user.id, role="admin")
        return {"message":"user promoted successfully"}

    async def Demote(self,email: str, current_user: TokenClaimUser):
        user=await self.repo.FindByEmail(email)
        if not user:
            raise NotFoundError("User not found")
        if current_user.role!="superadmin":
            raise PermissionError("insufficient permission")
        await self.repo.update_user(user.id, role="user")
        return {"message":"user demoted successfully"}

        

        
