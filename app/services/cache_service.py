from typing import Optional
from app.models import Channel, InternalError
from app.schemas import RegistrationDTO
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
            raise InternalError(
                internal_message=f"Failed reading env vars for CacheService because of missing key: {e}",
                public_message=f"Failed due to invalid server configuration."
            )
        except Exception as e:
            raise InternalError(
                internal_message=f"CacheService init failed because of unexpected error: {e}",
                public_message=f"Failed due to invalid server configuration."
            )

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
                try:
                    registration: RegistrationDTO = RegistrationDTO(**json_data["data"])
                except Exception as e:
                    raise InternalError(
                        internal_message=f"Failed valkey data mapping to RegistrationDTO object in method provided_code_correct because: {e}",
                        public_message="Failed provided code validation because of Server error."
                    )
                return registration

        return None
    
    
    def set_available_channels(self, channels: list[Channel]) -> None:
        channels_key = self._data_key_prefix + "available_channels"

        self._client.setex(channels_key, 5, json.dumps([asdict(channel) for channel in channels]))

    def get_available_channels(self) -> list[Channel]:
        channels_key = self._data_key_prefix + "available_channels"

        if self._client.exists(channels_key):
            saved_data = self._client.get(channels_key)
            json_data = json.loads(saved_data)

            try:
                channels: list[Channel] = [Channel(**channel) for channel in json_data]
            except Exception as e:
                raise InternalError(
                    internal_message=f"Failed valkey data mapping to Channel objects in method get_available_channels because: {e}",
                    public_message="Failed reading available channels because of Server error."
                )
            return channels
        
        return []
    


