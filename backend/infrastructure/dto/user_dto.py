from domain.models.user_model import User, UserRegister
from infrastructure.models.model import User as UserModel


def create_domain_user_from_model(user_model: UserModel) -> User:
    return User(
        id=user_model.id,
        username=user_model.username,
        hashed_password=user_model.hashed_password,
        verified=user_model.verified,
        role=user_model.role,
        email=user_model.email,
        assigned_tasks=[task.id for task in user_model.assigned_tasks],
        my_tasks=[task.id for task in user_model.my_tasks],
    )


def user_model_from_domain(domain_user: User) -> UserModel:
    return UserModel(
        id=domain_user.id,
        username=domain_user.username,
        email=domain_user.email,
        hashed_password=domain_user.hashed_password
        or getattr(domain_user, "hashed_password", None),
    )


def create_user_model_from_register(
    user_register: UserRegister, hashed_password: str
) -> UserModel:
    return UserModel(
        username=user_register.username,
        email=user_register.email,
        hashed_password=hashed_password,
    )
