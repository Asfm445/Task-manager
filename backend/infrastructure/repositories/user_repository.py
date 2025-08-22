from domain.interfaces.user_repo import IUserRepository
from domain.models.user_model import User as dUser
from domain.models.user_model import UserRegister
from infrastructure.dto.user_dto import create_domain_user_from_model
from infrastructure.models.model import User as UserModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def FindByEmail(self, email: str)-> dUser:
        try:
            result = await self.db.execute(
                select(UserModel)
                .where(UserModel.email == email)
                .limit(1)
            )
            result=result.scalars().first()
            return create_domain_user_from_model(result)if result else None
        except Exception as e:
            print(f"FindByEmail error: {e}")
            raise

    
    async def FindByUsername(self, username: str)-> dUser:
        try:
            result = await self.db.execute(
                select(UserModel)
                .where(UserModel.username== username)
                .limit(1)
            )
            result=result.scalars().first()
            return create_domain_user_from_model(result)if result else None
        except Exception as e:
            print(f"FindByEmail error: {e}")
            raise

    async def Create(self, user: UserRegister, hashed_password: str, role: str):
        try:
            db_user = UserModel(
                username=user.username,
                email=user.email,
                hashed_password=hashed_password,
                role=role
            )
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            return  create_domain_user_from_model(db_user)
        except Exception as e:
            await self.db.rollback()
            print(f"Create user error: {e}")        
            raise
    async def update_user(self, user_id: int, **kwargs)-> dUser:
        """
        Update any fields of a user dynamically.
        Example: await repo.update_user(1, verified=True, hashed_password="...")
        """
        if not kwargs:
            return None  # nothing to update

        await self.db.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(**kwargs)
        )
        await self.db.commit()

        result = await self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return create_domain_user_from_model(result.scalar_one_or_none())
    async def get_all_users(self):
        """
        Fetch all users from the database.
        Returns a list of UserModel objects.
        """
        try:
            result = await self.db.execute(select(UserModel))
            users = result.scalars().all() 
            return [create_domain_user_from_model(user) for user in users] if result else []
        except Exception as e:
            print(f"get_all_users error: {e}")
            raise


        