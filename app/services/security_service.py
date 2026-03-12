import os
from pathlib import Path
from argon2 import PasswordHasher
from dotenv import load_dotenv

class SecurityService:
    def __init__(self):
        self._hasher = PasswordHasher()
        try:
            load_dotenv(Path(__file__).parent.parent.parent / ".env")

            self._pepper = os.environ["PEPPER"]

        except KeyError as e:
            raise e

    def get_password_hash(self, password: str) -> str:
        password = password + self._pepper
        return self._hasher.hash(password)