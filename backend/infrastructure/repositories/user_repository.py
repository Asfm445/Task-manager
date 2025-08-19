from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.Models import UserRegister
from infrastructure.models.model import User as UserModel
from domain.repositories.user_repo import IUserRepository

class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def FindByEmail(self, email: str):
        try:
            result = await self.db.execute(
                select(UserModel)
                .where(UserModel.email == email)
                .limit(1)
            )
            return result.scalars().first()
        except Exception as e:
            print(f"FindByEmail error: {e}")
            raise
    async def FindByUsername(self, username: str):
        try:
            result = await self.db.execute(
                select(UserModel)
                .where(UserModel.username== username)
                .limit(1)
            )
            return result.scalars().first()
        except Exception as e:
            print(f"FindByEmail error: {e}")
            raise

    async def Create(self, user: UserRegister, hashed_password: str):
        try:
            db_user = UserModel(
                username=user.username,
                email=user.email,
                hashed_password=hashed_password
            )
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            return {"message":"user registered successfully"}
        except Exception as e:
            await self.db.rollback()
            print(f"Create user error: {e}")
            raise