from abc import ABC, abstractmethod
from domain.Models import  UserRegister

# Abstract Interface for UserRepository
class IUserRepository(ABC):
    @abstractmethod
    async def FindByEmail(self, email: str):
        pass
    @abstractmethod
    async def FindByUsername(self, username: str):
        pass

    @abstractmethod
    async def Create(self, user: UserRegister, hashed_password: str):
        pass