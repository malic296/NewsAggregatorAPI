from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
import jwt
from jwt import PyJWTError
from argon2.exceptions import VerificationError, VerifyMismatchError, InvalidHashError
from app.models import Consumer

class SecurityService:
    def __init__(self, pepper: str, jwt: str):
        self._hasher = PasswordHasher()
        self._pepper = pepper
        self._secret_key = jwt
        self._algorithm = "HS256"

    def get_password_hash(self, password: str) -> str:
        password = password + self._pepper
        return self._hasher.hash(password)

    def verify_password(self, hashed_password: str, plain_password: str) -> bool:
        try:
            self._hasher.verify(hashed_password, plain_password + self._pepper)
        except (InvalidHashError, VerificationError, VerifyMismatchError):
            return False

        return True

    def is_password_identical_to_hash(self, hashed_password: str, plain_password: str) -> bool:
        try:
            return self._hasher.verify(hashed_password, plain_password + self._pepper)
        except (InvalidHashError, VerificationError, VerifyMismatchError):
            return False

    def create_access_token(self, consumer: Consumer) -> str:
        data = asdict(consumer)
        data.pop("id", None)
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str):
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except PyJWTError:
            return None

