from abc import ABC, abstractmethod
from domain.models.user_model import  UserRegister, User as dUser

# Abstract Interface for UserRepository
class IUserRepository(ABC):
    @abstractmethod
    async def FindByEmail(self, email: str):
        pass
    @abstractmethod
    async def FindByUsername(self, username: str):
        pass

    @abstractmethod
    async def Create(self, user: UserRegister, hashed_password: str, role: str):
        pass
    @abstractmethod
    async def update_user(self, user_id: int, **kwargs):
        pass

    @abstractmethod
    async def get_all_users(self):
        pass

    @abstractmethod
    async def CheckEmailAndUsername(self, email: str, username) -> bool:
        pass

    @abstractmethod
    async def find_by_id(self, user_id: int) -> dUser:
        pass