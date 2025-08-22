from api.schemas.user_schema import LoginInput, UserCreate
from domain.models.user_model import UserLogin, UserRegister


def user_create_to_domain(userCreateInput: UserCreate)-> UserRegister:
    return UserRegister(username=userCreateInput.username, email=userCreateInput.email, password=userCreateInput.password)

def user_login_to_domain(login_input: LoginInput)->UserLogin:
    return UserLogin(email=login_input.email, password=login_input.password)