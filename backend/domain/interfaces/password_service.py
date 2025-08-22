from abc import ABC, abstractmethod


class IPasswordService(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a plain password and return the hashed value"""
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify that a plain password matches the hashed one"""
        pass
