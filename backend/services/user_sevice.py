from domain.exceptions import BadRequestError, NotFoundError
from domain.Models import UserLogin, UserRegister


class UserService:
    def __init__(self, repo, pass_service, jwt_service):
        self.repo = repo
        self.pass_service = pass_service
        self.jwt_service = jwt_service

    def Register(self, user: UserRegister):
        if self.repo.FindByEmail(user.email):
            raise BadRequestError("Email already exist")
        user.password = self.pass_service.hash_password(user.password)
        registered_user = self.repo.Create(user.__dict__)
        return registered_user

    def Login(self, user_info: UserLogin):
        user = self.repo.FindByEmail(user_info.email)
        if not user:
            raise NotFoundError("User not found")
        if not self.pass_service.verify_password(user_info.password, user.password):
            raise BadRequestError("Invalid password")
        access_token = self.jwt_service.create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
