from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from argon2 import PasswordHasher
from dotenv import load_dotenv
import jwt
from jwt import PyJWTError


class SecurityService:
    def __init__(self):
        self._hasher = PasswordHasher()
        try:
            load_dotenv(Path(__file__).parent.parent.parent / ".env")

            self._pepper = os.environ["PEPPER"]
            self._secret_key = os.environ["JWT_SECRET"]
            self._algorithm = "HS256"

        except KeyError as e:
            raise e

    def get_password_hash(self, password: str) -> str:
        password = password + self._pepper
        return self._hasher.hash(password)

    def verify_password(self, hashed_password: str, plain_password: str) -> bool:
        try:
            return self._hasher.verify(hashed_password, plain_password + self._pepper)
        except Exception as e:
            return False



    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str):
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except PyJWTError:
            return None

