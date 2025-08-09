from domain.Models import User, UserRegister
from infrastructure.models.dto import (
    create_domain_user_from_model,
    create_user_model_from_register,
)
from infrastructure.models.model import User as UserModel
from sqlalchemy.orm import Session


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def FindByEmail(self, email: str):
        dbuser = self.db.query(UserModel).filter(UserModel.email == email).first()
        if not dbuser:
            return None
        return create_domain_user_from_model(dbuser)

    def Create(self, user: UserRegister, hashed_password: str):
        db_user = create_user_model_from_register(user, hashed_password)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return {"message": "User created successfully"}
