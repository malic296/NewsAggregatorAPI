import json

import redis
from dotenv import load_dotenv
from pathlib import Path
import os
from app.schemas.registration_dto import RegistrationDTO


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

    def is_registration_pending(self, registration: RegistrationDTO) -> bool:
        email_key = f"reg:data:{registration.email}"
        username_key = f"reg:lock:user:{registration.username}"

        exists_count = self._client.exists(email_key, username_key)
        return exists_count > 0

    def delete_registration_from_pending(self, registration: RegistrationDTO) -> None:
        email_key = f"reg:data:{registration.email}"
        username_key = f"reg:lock:user:{registration.username}"

        raw_data = self._client.get(email_key)

        pipe = self._client.pipeline()

        if raw_data:
            old_data=json.loads(raw_data)
            old_username = old_data.get("username")
            pipe.delete(f"reg:lock:user:{old_username}")

        pipe.delete(email_key)
        pipe.delete(username_key)
        pipe.execute()

    def create_pending_registration(self, registration: RegistrationDTO, code: int) -> None:
        data_key = f"reg:data:{registration.email}"
        lock_key = f"reg:lock:user:{registration.username}"

        storage_data = registration.model_dump()
        storage_data["code"] = code

        expiry = 60

        pipe = self._client.pipeline()
        pipe.setex(data_key, expiry, json.dumps(storage_data))
        pipe.setex(lock_key, expiry, "locked")
        pipe.execute()
