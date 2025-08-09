from domain.Models import Token as DMToken
from infrastructure.models.model import Token
from sqlalchemy.orm import Session


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def FindByID(self, id: str):
        dbtoken = self.db.query(Token).filter(Token.id == id).first()
        if not dbtoken:
            return None
        return [
            DMToken(
                dbtoken.id,
                dbtoken.token,
                dbtoken.user_id,
                dbtoken.created_at,
                dbtoken.expired_at,
            ),
            dbtoken.user,
        ]

    def Create(self, token: dict):
        db_token = Token(**token)
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return {"token": "token created successfully"}
