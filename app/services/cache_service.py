import json
import redis
from dotenv import load_dotenv
from pathlib import Path
import os

class CacheService:
    def __init__(self):

        try:
            load_dotenv(Path(__file__).parent.parent.parent / ".env")

            host = os.environ["REDIS_HOST"]
            port = int(os.environ["REDIS_PORT"])
            db = int(os.environ["REDIS_DB"])

            self._client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True
            )
        except KeyError as e:
            raise e
        except Exception as e:
            raise e

    def is_registration_pending(self, email: str) -> bool:
        email_key = f"reg:email:{email}"

        exists_count = self._client.exists(email_key)
        return exists_count > 0

    def delete_registration_from_pending(self, email: str) -> None:
        email_key = f"reg:email:{email}"

        if self._client.exists(email_key):
            self._client.delete(email_key)

    def create_pending_registration(self, email: str, code: int) -> None:
        email_key = f"reg:email:{email}"

        if not self._client.exists(email_key):
            self._client.setex(email_key, 120, code)

    def provided_code_correct(self, email: str, code: int) -> bool:
        email_key = f"reg:email:{email}"

        if self._client.exists(email_key):
            saved_code = self._client.get(email_key)

            if int(saved_code) == code:
                self._client.delete(email_key)
                return True

        return False

