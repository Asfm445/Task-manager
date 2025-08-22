from domain.models.user_model import Token as DMToken
from infrastructure.models.model import Token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from domain.interfaces.token_repo import ITokenRepository
from sqlalchemy.orm import selectinload


class TokenRepository(ITokenRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def FindByID(self, id: str):
        result = await self.db.execute(
            select(Token)
            .options(selectinload(Token.user))  # preloads user relationship
            .where(Token.id == id)
        )
        dbtoken = result.scalar_one_or_none()  # returns single object or None
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
            dbtoken.user,  # already loaded
        ]

    async def Create(self, token: dict):
        db_token = Token(**token)
        self.db.add(db_token)
        await self.db.commit()
        await self.db.refresh(db_token)
        return {"token": "token created successfully"}
    
    async def DeleteByID(self, id: str):
        """Delete a token by its ID"""
        result = await self.db.execute(
            select(Token).where(Token.id == id)
        )
        dbtoken = result.scalar_one_or_none()
        if not dbtoken:
            return {"error": f"Token with id {id} not found"}

        await self.db.delete(dbtoken)
        await self.db.commit()
        return {"message": f"Token with id {id} deleted successfully"}
