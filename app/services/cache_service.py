from typing import Optional
from app.models import Channel
from app.schemas.registration_dto import RegistrationDTO
import redis
from dotenv import load_dotenv
from pathlib import Path
import os
import json
from dataclasses import asdict

class CacheService:
    def __init__(self):
        self._reg_key_prefix = "reg:"
        self._data_key_prefix = "data:"

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
        email_key = self._reg_key_prefix + registration.email

        exists_count = self._client.exists(email_key)
        return exists_count > 0

    def delete_registration_from_pending(self, registration: RegistrationDTO) -> None:
        email_key = self._reg_key_prefix + registration.email

        if self._client.exists(email_key):
            self._client.delete(email_key)

    def create_pending_registration(self, registration: RegistrationDTO, code: int) -> None:
        email_key = self._reg_key_prefix + registration.email

        if not self._client.exists(email_key):
            dict_data = {
                "code": code,
                "data": registration.model_dump()
            }

            self._client.setex(email_key, 120, json.dumps(dict_data))


    def provided_code_correct(self, email: str, code: int) -> Optional[RegistrationDTO]:
        email_key = self._reg_key_prefix + email

        if self._client.exists(email_key):
            saved_data = self._client.get(email_key)
            json_data = json.loads(saved_data)

            if int(json_data["code"]) == code:
                self._client.delete(email_key)
                return RegistrationDTO(**json_data["data"])

        return None
    
    
    def set_available_channels(self, channels: list[Channel]) -> None:
        channels_key = self._data_key_prefix + "available_channels"

        self._client.setex(channels_key, 5, json.dumps([asdict(channel) for channel in channels]))

    def get_available_channels(self) -> list[Channel]:
        channels_key = self._data_key_prefix + "available_channels"

        if self._client.exists(channels_key):
            saved_data = self._client.get(channels_key)
            json_data = json.loads(saved_data)

            return [Channel(**channel) for channel in json_data]
        
        return []
    


