from abc import ABC, abstractmethod
from typing import Optional, Tuple
from domain.Models import Token as DMToken


class ITokenRepository(ABC):
    @abstractmethod
    async def FindByID(self, id: str) -> Optional[Tuple[DMToken, object]]:
        """Find a token by its ID and return a tuple (DMToken, user) or None if not found."""
        pass

    @abstractmethod
    async def Create(self, token: dict) -> dict:
        """Create a new token in the database."""
        pass
