import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from domain.exceptions import BadRequestError
from domain.models.user_model import Token
from jose import ExpiredSignatureError, JWTError, jwt
from domain.interfaces.jwt_service import JwtServiceInterface


class JwtService(JwtServiceInterface):
    def __init__(
        self,
        SECRET_KEY: str,
        ALGORITHM,
        ACCESS_TOKEN_EXPIRE_MINUTES: int,
        REFRESH_TOKEN_EXPIRE_HOURS: int,
    ):
        self.SECRET_KEY = SECRET_KEY
        self.ALGORITHM = ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
        self.REFRESH_TOKEN_EXPIRE_HOURS = REFRESH_TOKEN_EXPIRE_HOURS

    def create_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=1))
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def decode_token(self, token: str):
        try:
            return jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM]), None
        except ExpiredSignatureError:
            return None, "token is expired!"
        except JWTError:
            return None, "token is invalid"

    def create_access_token(self, data: dict):
        return self.create_token(
            data, expires_delta=timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    def create_refresh_token(self, data: dict):
        token_id = str(uuid.uuid4())
        data = {**data, "id": token_id}
        token = self.create_token(
            data, expires_delta=timedelta(hours=self.REFRESH_TOKEN_EXPIRE_HOURS)
        )
        return Token(
            token_id,
            token,
            data["user_id"],
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
            + timedelta(hours=self.REFRESH_TOKEN_EXPIRE_HOURS),
        )
    def create_verification_token(self, data: dict):
        token_id = str(uuid.uuid4())
        data = {**data, "id": token_id}
        token = self.create_token(
            data, expires_delta=timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {
            "id": token_id,
            "token": token,
            "expired_at":datetime.now(timezone.utc),
            "expired_at":datetime.now(timezone.utc)
            + timedelta(hours=self.REFRESH_TOKEN_EXPIRE_HOURS),
        }

    def hash_token(self, token: str):
        return hashlib.sha256(token.encode()).hexdigest()

    def verify_token(self, token: str, hashed: str):
        return self.hash_token(token) == hashed
