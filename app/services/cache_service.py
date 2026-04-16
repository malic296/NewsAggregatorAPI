from typing import Optional
from app.models import Channel, Article
from app.core.errors import DependencyUnavailableError, MappingError
from app.schemas import RegistrationDTO
from redis import Redis
from redis.exceptions import RedisError
import json
from dataclasses import asdict
from redis.retry import Retry
from redis.backoff import NoBackoff
from app.core.settings import settings

class CacheService:
    def __init__(self):
        self._reg_key_prefix = "reg:"
        self._data_key_prefix = "data:"

        try:
            self._client = Redis(
                host=settings.cache.HOST,
                port=settings.cache.PORT,
                db=settings.cache.DATABASE,
                decode_responses=True,
                retry=Retry(NoBackoff(), 0),
                socket_connect_timeout=2.0
            )

            self._client.ping()

        except RedisError as e:
            raise DependencyUnavailableError(dependency="VALKEY")

    def is_registration_pending(self, registration: RegistrationDTO) -> bool:
        email_key = self._reg_key_prefix + registration.email

        data = self._client.get(email_key)
        return data is not None

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
                return RegistrationDTO(**json_data["data"])

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
            json_data = json.loads(saved_data)
            try:
                return [Channel(**channel) for channel in json_data]
            except Exception as e:
                raise MappingError(mapping_error=str(e), method="get_available_channels")
        
        return []

    def get_article(self, uuid: str) -> Optional[Article]:
        article_key = self._data_key_prefix + uuid
        saved_data = self._client.get(article_key)
        if saved_data:
            json_data = json.loads(saved_data)
            try:
                return Article(**json_data)
            except Exception as e:
                raise MappingError(mapping_error=str(e), method="get_article")
        else:
            return None

    def set_article(self, article: Article) -> Optional[Article]:
        article_key = self._data_key_prefix + article.uuid
        try:
            article_dict = asdict(article)
            article_dict["pub_date"] = article_dict["pub_date"].isoformat()
            data = json.dumps(article_dict)
            self._client.setex(article_key, 600, data)

        except Exception as e:
            raise MappingError(mapping_error=str(e), method="set_article")

    def can_request_go_through(self, user_key: str) -> bool:
        requests = self._client.incr(user_key)

        if requests == 1:
            self._client.expire(user_key, 5)

        return requests <= 3


