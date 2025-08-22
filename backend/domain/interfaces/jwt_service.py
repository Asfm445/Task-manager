
# domain/interfaces/jwt_service.py
from typing import Protocol, Optional, Tuple
from datetime import timedelta
from domain.models.user_model import Token


class JwtServiceInterface(Protocol):
    def create_token(self, data: dict, expires_delta: timedelta = None) -> str:
        ...

    def decode_token(self, token: str) -> Tuple[Optional[dict], Optional[str]]:
        ...

    def create_access_token(self, data: dict) -> str:
        ...

    def create_refresh_token(self, data: dict) -> Token:
        ...

    def create_verification_token(self, data: dict) -> dict:
        ...

    def hash_token(self, token: str) -> str:
        ...

    def verify_token(self, token: str, hashed: str) -> bool:
        ...
