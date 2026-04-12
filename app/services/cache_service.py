from json import JSONDecodeError
from typing import Optional
from app.models import Channel, Article
from app.core.errors import InternalError
from app.schemas import RegistrationDTO
from redis import Redis
from redis.exceptions import RedisError
from dotenv import load_dotenv
from pathlib import Path
import os
import json
from dataclasses import asdict
from redis.retry import Retry
from redis.backoff import NoBackoff

class CacheService:
    def __init__(self):
        self._reg_key_prefix = "reg:"
        self._data_key_prefix = "data:"

        try:
            load_dotenv(Path(__file__).parent.parent.parent / ".env")

            host = os.environ["REDIS_HOST"]
            port = int(os.environ["REDIS_PORT"])
            db = int(os.environ["REDIS_DB"])

            self._client = Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                retry=Retry(NoBackoff(), 0),
                socket_connect_timeout=2.0
            )

            self._client.ping()

        except KeyError as e:
            raise InternalError(
                internal_message=f"Failed reading env vars for CacheService because of missing key: {e}"
            )

        except RedisError as e:
            raise InternalError(
                internal_message=f"Valkey failed in cache service init because: {e}"
            )

        except Exception as e:
            raise InternalError(
                internal_message=f"CacheService init failed because of unexpected error: {e}"
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

        saved_data = self._client.get(email_key)
        if saved_data:
            json_data = json.loads(saved_data)

            if int(json_data["code"]) == code:
                self._client.delete(email_key)
                try:
                    registration: RegistrationDTO = RegistrationDTO(**json_data["data"])
                except Exception as e:
                    raise InternalError(
                        internal_message=f"Failed valkey data mapping to RegistrationDTO object in method provided_code_correct because: {e}"
                    )
                return registration

        return None

    def set_available_channels(self, channels: list[Channel], user_id: int) -> None:
        channels_key = self._data_key_prefix + f"{user_id}:" + "available_channels"

        self._client.setex(channels_key, 600, json.dumps([asdict(channel) for channel in channels]))

    def invalidate_cache_channels(self, user_id: int) -> None:
        channels_key = self._data_key_prefix + f"{user_id}:" + "available_channels"
        self._client.delete(channels_key)

    def get_available_channels(self, user_id: int) -> list[Channel]:
        channels_key = self._data_key_prefix + f"{user_id}:" + "available_channels"

        saved_data = self._client.get(channels_key)
        if saved_data:
            try:
                json_data = json.loads(saved_data)
                channels: list[Channel] = [Channel(**channel) for channel in json_data]

            except JSONDecodeError as e:
                raise InternalError(
                    internal_message=f"Failed loading channels data from valkey to json in method get_available_channels because: {e}"
                )
            except Exception as e:
                raise InternalError(
                    internal_message=f"Failed valkey data mapping to Channel objects in method get_available_channels because: {e}"
                )
            return channels
        
        return []

    def get_article(self, uuid: str) -> Optional[Article]:
        article_key = self._data_key_prefix + uuid
        saved_data = self._client.get(article_key)
        if saved_data:
            try:
                json_data = json.loads(saved_data)
                article: Article = Article(**json_data)
                return article
            except (ConnectionError, TimeoutError):
                return None
            except Exception as e:
                raise InternalError(
                    internal_message=f"Failed loading Article from cache even though article was found because: {e}"
                )
        else:
            return None

    def set_article(self, article: Article) -> Optional[Article]:
        article_key = self._data_key_prefix + article.uuid
        try:
            data = json.dumps(asdict(article))
            self._client.setex(article_key, 600, data)

        except (ConnectionError, TimeoutError) as e:
            return None
        except Exception as e:
            raise InternalError(
                internal_message=f"Serialization failed for article because: {e}"
            )

    


