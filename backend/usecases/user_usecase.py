from domain.exceptions import BadRequestError, NotFoundError
from domain.Models import UserLogin, UserRegister


class UserUsecase:
    def __init__(self, repo, pass_service, jwt_service, tokenRepo):
        self.repo = repo
        self.pass_service = pass_service
        self.jwt_service = jwt_service
        self.tokenRepo = tokenRepo

    def Register(self, user: UserRegister):
        if self.repo.FindByEmail(user.email):
            raise BadRequestError("Email already exist")
        hashed_password = self.pass_service.hash_password(user.password)
        return self.repo.Create(user, hashed_password)

    def Login(self, user_info: UserLogin):
        user = self.repo.FindByEmail(user_info.email)
        if not user:
            raise NotFoundError("User not found")
        if not self.pass_service.verify_password(
            user_info.password, user.hashed_password
        ):
            raise BadRequestError("Invalid password")
        access_token = self.jwt_service.create_access_token(
            data={"username": user.username, "email": user.email}
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
        self.tokenRepo.Create(refresh_token.__dict__)
        return {
            "access_token": access_token,
            "refresh_token": tokenStr,
            "token_type": "bearer",
        }

    def getUserByEmail(self, email):
        user = self.repo.FindByEmail(email)
        if not user:
            raise NotFoundError("User not found")
        return user

    def RefreshToken(self, token):
        payload = self.jwt_service.decode_token(token)
        if not payload:
            raise BadRequestError("Invalid token")

        result = self.tokenRepo.FindByID(payload["id"])
        if not result:
            raise BadRequestError("Invalid token")

        dbtoken, user = result
        if not self.jwt_service.verify_token(token, dbtoken.token):
            raise BadRequestError("Invalid token")

        # Optional extra check for stolen tokens
        if user.id != payload.get("user_id"):
            raise BadRequestError("Token-user mismatch")

        access_token = self.jwt_service.create_access_token(
            data={"username": user.username, "email": user.email}
        )
        return {"access_token": access_token}
        return {"access_token": access_token}
        return {"access_token": access_token}
        return {"access_token": access_token}
        return {"access_token": access_token}
        return {"access_token": access_token}
        return {"access_token": access_token}
