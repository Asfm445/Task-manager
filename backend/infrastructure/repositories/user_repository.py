from infrastructure.models.model import User
from sqlalchemy.orm import Session


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def FindByEmail(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def Create(self, user: dict):
        db_user = User(**user)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
